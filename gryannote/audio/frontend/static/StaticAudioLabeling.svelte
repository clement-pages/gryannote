<script lang="ts">
	import { uploadToHuggingFace } from "@gradio/utils";
	import { Empty, IconButton } from "@gradio/atoms";
	import { ShareButton, BlockLabel } from "@gradio/atoms";
	import { Download, Music } from "@gradio/icons";
	import type { I18nFormatter } from "@gradio/utils";
	import AudioPlayer from "../player/AudioPlayer.svelte";
	import VideoPlayer from "../player/VideoPlayer.svelte";
	import { createEventDispatcher } from "svelte";
	import type { WaveformOptions, TimelineOptions, HoverOptions } from "../shared/types";
	import AnnotatedAudioData from "../shared/AnnotatedAudioData";
    import { DownloadLink } from "@gradio/wasm/svelte";

	export let value: null | AnnotatedAudioData = null;
	export let label: string;
	export let show_label = true;
	export let show_download_button: boolean = true;
	export let show_minimap: boolean = true;
	export let i18n: I18nFormatter;
	export let waveform_settings: Record<string, any>;
	export let waveform_options: WaveformOptions = {};
	export let timeline_options: TimelineOptions = {};
	export let hover_options: HoverOptions = {};

	let show_share_button: boolean = false;
	let video: HTMLVideoElement | undefined;

	const dispatch = createEventDispatcher<{
		change: typeof value;
		play: undefined;
		pause: undefined;
		end: undefined;
		stop: undefined;
	}>();

	$: value && dispatch("change", value);
</script>

<BlockLabel
	{show_label}
	Icon={Music}
	float={false}
	label={label || i18n("audio.audio")}
/>

{#if value !== null}
	<div class="icon-buttons">
		{#if show_download_button && value.file_data !== null}
			<div class="download-button">
				<DownloadLink
					href={value.file_data.url}
					download={value.file_data.orig_name || value.file_data.path}
				>
					<IconButton Icon={Download} label={i18n("common.download")}/>
				</DownloadLink>
			</div>
		{/if}
		{#if show_share_button}
			<ShareButton
				{i18n}
				on:error
				on:share
				formatter={async (value) => {
					if (!value) return "";
					let url = await uploadToHuggingFace(value.url, "url");
					return `<audio controls src="${url}"></audio>`;
				}}
				{value}
			/>
		{/if}
	</div>
	<!--TODO: do not hardcore following format list-->
	{#if ["mp4", "avi", "webm", "mov",].includes(value.file_data.url.split(".").pop())}
		<VideoPlayer
			bind:node={video}
			src={value.file_data.url}
			preload="auto"
			autoplay={false}
			muted={true}
		/>
	{/if}
	<AudioPlayer
		isDialogOpen={false}
		value={value}
		interactive={false}
		{label}
		{i18n}
		{show_minimap}
		{waveform_settings}
		{waveform_options}
		{timeline_options}
		{hover_options}
		on:stop
		on:play={() => video?.play()}
		on:pause={() => video?.pause()}
		on:timeupdate={(e) => {
			if(video) video.currentTime = e.detail;
		}}
	/>
{:else}
	<Empty size="small">
		<Music />
	</Empty>
{/if}

<style>
	.icon-buttons {
		display: flex;
		position: absolute;
		top: 6px;
		right: 6px;
		gap: var(--size-1);
	}
</style>
