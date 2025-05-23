<script lang="ts">
	import { getContext, onDestroy, createEventDispatcher } from "svelte";
	import { Upload, ModifyUpload } from "@gradio/upload";
	import {
		prepare_files, FileData,
		type upload_files,
		type Client
	} from "@gradio/client";
	import { BlockLabel } from "@gradio/atoms";
	import { Music } from "@gradio/icons";
	import AnnotatedAudioData from "../shared/AnnotatedAudioData"
	import type { IBlobEvent, IMediaRecorder } from "extendable-media-recorder";
	import WaveSurfer from "@gryannote/wavesurfer.js";
	import type { I18nFormatter } from "@gradio/utils";
	import AudioRecorder from "../recorder/AudioRecorder.svelte";
	import StreamAudio from "../streaming/StreamAudio.svelte";
	import { SelectSource } from "@gradio/atoms";
	import type { WaveformOptions, TimelineOptions, HoverOptions } from "../shared/types";
	import Help  from "../shared/icons/Help.svelte"
	import HelpDialog from "../shared/HelpDialog.svelte";
    import AudioPlayer from "../player/AudioPlayer.svelte";
	import VideoPlayer from "../player/VideoPlayer.svelte";

	export let value: null | AnnotatedAudioData = null;
	export let label: string;
	export let root: string;
	export let show_label = true;
	export let show_download_button: boolean = true;
	export let sources:
		| ["microphone"]
		| ["upload"]
		| ["microphone", "upload"]
		| ["upload", "microphone"] = ["microphone", "upload"];
	export let pending = false;
	export let streaming = false;
	export let i18n: I18nFormatter;
	export let show_minimap: boolean = true;
	export let waveform_settings: Record<string, any>;
	export let waveform_options: WaveformOptions = {};
	export let timeline_options: TimelineOptions = {};
	export let hover_options: HoverOptions = {};
	export let dragging: boolean;
	export let active_source: "microphone" | "upload";
	export let max_file_size: number | null = null;
	export let upload: Client["upload"];
	export let stream_handler: Client["stream"];

	// Needed for wasm support
	const upload_fn = getContext<typeof upload_files>("upload_files");

	$: dispatch("drag", dragging);

	// TODO: make use of this
	// export let type: "normal" | "numpy" = "normal";
	let recording = false;
	let recorder: IMediaRecorder;
	let mode = "";
	let header: Uint8Array | undefined = undefined;
	let pending_stream: Uint8Array[] = [];
	let submit_pending_stream_on_pending_end = false;
	let inited = false;

	let waveform: WaveSurfer | undefined;

	let video: HTMLVideoElement | undefined;
	let videoCurrentTime: number = 0.;
	let videoURL: string | undefined;
	$: if(!videoURL && value?.file_data?.mime_type?.includes("video")){
		videoURL = value.file_data.url;
	}

	let isDialogOpen = false;
	let helpDialog: HelpDialog;

	const STREAM_TIMESLICE = 500;
	const NUM_HEADER_BYTES = 44;
	let audio_chunks: Blob[] = [];
	let module_promises: [
		Promise<typeof import("extendable-media-recorder")>,
		Promise<typeof import("extendable-media-recorder-wav-encoder")>
	];

	function get_modules(): void {
		module_promises = [
			import("extendable-media-recorder"),
			import("extendable-media-recorder-wav-encoder")
		];
	}

	if (streaming) {
		get_modules();
	}

	const dispatch = createEventDispatcher<{
		change: AnnotatedAudioData | null;
		stream: AnnotatedAudioData;
		edit: typeof value;
		play: never;
		pause: never;
		stop: never;
		end: never;
		drag: boolean;
		error: string;
		upload: FileData;
		clear: undefined;
		start_recording: undefined;
		pause_recording: undefined;
		stop_recording: undefined;
	}>();

	const dispatch_blob = async (
		blobs: Uint8Array[] | Blob[],
		event: "stream" | "change" | "stop_recording"
	): Promise<void> => {
		let _audio_blob = new File(blobs, "audio.wav");
		const val = await prepare_files([_audio_blob], event === "stream");
		let fileData = (
			(await upload(val, root, undefined, max_file_size || undefined))?.filter(
				Boolean
			) as FileData[]
		)[0];
		if(value === null){
			value = new AnnotatedAudioData(fileData);
		}
		else{
			value.file_data = fileData;
		}
		dispatch(event, value);
	};

	onDestroy(() => {
		if (streaming && recorder && recorder.state !== "inactive") {
			recorder.stop();
		}
	});

	async function prepare_audio(): Promise<void> {
		let stream: MediaStream | null;

		try {
			stream = await navigator.mediaDevices.getUserMedia({ audio: true });
		} catch (err) {
			if (!navigator.mediaDevices) {
				dispatch("error", i18n("audio.no_device_support"));
				return;
			}
			if (err instanceof DOMException && err.name == "NotAllowedError") {
				dispatch("error", i18n("audio.allow_recording_access"));
				return;
			}
			throw err;
		}
		if (stream == null) return;
		if (streaming) {
			const [{ MediaRecorder, register }, { connect }] = await Promise.all(
				module_promises
			);
			await register(await connect());
			recorder = new MediaRecorder(stream, { mimeType: "audio/wav" });
			recorder.addEventListener("dataavailable", handle_chunk);
		} else {
			recorder = new MediaRecorder(stream);
			recorder.addEventListener("dataavailable", (event) => {
				audio_chunks.push(event.data);
			});
			recorder.addEventListener("stop", async () => {
				recording = false;
				await dispatch_blob(audio_chunks, "change");
				await dispatch_blob(audio_chunks, "stop_recording");
				audio_chunks = [];
			});
		}
		inited = true;
	}

	async function handle_chunk(event: IBlobEvent): Promise<void> {
		let buffer = await event.data.arrayBuffer();
		let payload = new Uint8Array(buffer);
		if (!header) {
			header = new Uint8Array(buffer.slice(0, NUM_HEADER_BYTES));
			payload = new Uint8Array(buffer.slice(NUM_HEADER_BYTES));
		}
		if (pending) {
			pending_stream.push(payload);
		} else {
			let blobParts = [header].concat(pending_stream, [payload]);
			dispatch_blob(blobParts, "stream");
			pending_stream = [];
		}
	}

	$: if (submit_pending_stream_on_pending_end && pending === false) {
		submit_pending_stream_on_pending_end = false;
		if (header && pending_stream) {
			let blobParts: Uint8Array[] = [header].concat(pending_stream);
			pending_stream = [];
			dispatch_blob(blobParts, "stream");
		}
	}

	async function record(): Promise<void> {
		recording = true;
		dispatch("start_recording");
		if (!inited) await prepare_audio();
		header = undefined;
		if (streaming) {
			recorder.start(STREAM_TIMESLICE);
		}
	}

	function clear(): void {
		dispatch("change", null);
		dispatch("clear");
		mode = "";
		value = null;
		videoURL = "";

		if(waveform) waveform.destroy();
	}

	function handle_load({ detail }: { detail: FileData }): void {
		value = new AnnotatedAudioData(detail);
		dispatch("change", value);
		dispatch("upload", detail);
	}

	function stop(): void {
		recording = false;

		if (streaming) {
			dispatch("stop_recording");
			recorder.stop();
			if (pending) {
				submit_pending_stream_on_pending_end = true;
			}
			dispatch_blob(audio_chunks, "stop_recording");
			dispatch("clear");
			mode = "";
		}
	}
</script>

<BlockLabel
	{show_label}
	Icon={Music}
	float={active_source === "upload" && value === null}
	label={label || i18n("audio.audio")}
/>
{#if value === null || streaming}
	{#if active_source === "microphone"}
		<ModifyUpload {i18n} on:clear={clear} absolute={true} />
		{#if streaming}
			<StreamAudio
				{record}
				{recording}
				{stop}
				{i18n}
				{waveform_settings}
				{waveform_options}
			/>
		{:else}
			<AudioRecorder
				bind:mode
				{i18n}
				{dispatch_blob}
				{waveform_settings}
				{waveform_options}
			/>
		{/if}
	{:else if active_source === "upload"}
		<!-- explicitly listed out audio mimetypes due to iOS bug not recognizing audio/* -->
		<Upload
			filetype="audio/aac,audio/midi,audio/mpeg,audio/ogg,audio/wav,audio/x-wav,audio/opus,audio/webm,audio/flac,audio/vnd.rn-realaudio,audio/x-ms-wma,audio/x-aiff,audio/amr,audio/*,video/mp4,video/mpeg,video/x-msvideo,video/ogg,video/webm,video/mp2t,video/3gpp,video/*"
			on:load={handle_load}
			bind:dragging
			on:error={({ detail }) => dispatch("error", detail)}
			{root}
			{max_file_size}
			{upload}
			{stream_handler}
		>
			<slot />
		</Upload>
	{/if}
{:else}
	<ModifyUpload
		{i18n}
		download={show_download_button ? value.file_data.url : null}
		on:clear={clear}
		on:edit={() => (mode = "edit")}
		absolute={true}
	/>

	{#if videoURL}
		<VideoPlayer
			bind:node={video}
			bind:currentTime={videoCurrentTime}
			src={videoURL}
			preload="auto"
			autoplay={false}
			muted={true}
		/>
	{/if}

	<AudioPlayer
		bind:mode
		bind:isDialogOpen
		bind:waveform
		{value}
		{label}
		{i18n}
		{show_minimap}
		{waveform_settings}
		{waveform_options}
		{timeline_options}
		{hover_options}
		interactive
		on:stop
		on:play={() => video?.play()}
		on:pause={() => video?.pause()}
		on:edit={(e) => dispatch("edit", e.detail)}
		on:timeupdate={(e) => {
			if(video) video.currentTime = e.detail
		}}
	/>
{/if}

<div class="button-zone">
	<a href="https://github.com/clement-pages/gryannote" id="logo-link">
		<img src="https://github.com/clement-pages/gryannote/blob/main/docs/assets/logo-gryannote.png?raw=true" alt=" " id="logo">
		<p> provided by gryannote</p>
	</a>
	<div id="select-source">
		<SelectSource {sources} bind:active_source handle_clear={clear}/>
	</div>
	<button
		id="help-button"
		title="help"
		on:click={() => helpDialog.openDialog()}
	>
		<Help/>
	</button>
</div>

<HelpDialog
    bind:this={helpDialog}
    bind:isOpen={isDialogOpen}
/>

<style>
	.button-zone{
		display: grid;
		grid-template-columns: 1fr 10fr 1fr;
		gap: 20px;
		align-items: center;
	}

	#logo-link{
		display: flex;
		flex-direction: row;
		font-family: inherit;
		font-size: 0.75em;
	}

	#logo {
		width: 2em;
		margin: 0.5em;
	}

	#logo-link:hover {
		color: var(--color-accent);
	}

	#select-source {
		grid-column: 2 / 3;
	}

	#help-button {
		width: 24px;
		height: 24px;
		grid-column: 3 / 4;
		color: var(--neutral-400);
	}

	#help-button:hover {
		color: var(--color-accent);
	}
</style>
