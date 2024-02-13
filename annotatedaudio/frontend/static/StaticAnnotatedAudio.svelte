<script lang="ts">
	import { uploadToHuggingFace } from "@gradio/utils";
	import { Empty } from "@gradio/atoms";
	import { ShareButton, IconButton, BlockLabel } from "@gradio/atoms";
	import { Download, Music } from "@gradio/icons";
	import type { I18nFormatter } from "@gradio/utils";
	import AudioPlayerWithAnnotation from "../player/AudioPlayerWithAnnotation.svelte";
	import { createEventDispatcher } from "svelte";
	import { DownloadLink } from "@gradio/wasm/svelte";
	import type { WaveformOptions} from "../shared/types";
	import AnnotatedAudioData from "../shared/AnnotatedAudioData";

	export let value: null | AnnotatedAudioData = null;
	export let label: string;
	export let show_label = true;
	export let enable_download_button: boolean = true;
	export let enable_share_button: boolean = true;
	export let i18n: I18nFormatter;
	export let waveform_settings: Record<string, any>;
	export let waveform_options: WaveformOptions;

	let show_download_button: boolean = true;
	let show_share_button: boolean = false;

	$: show_download_button = ((value?.rttm !== null) && enable_download_button);
	$: show_share_button = ((value?.rttm !== null) && enable_share_button)

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
		{#if show_download_button}
			<DownloadLink href={value.rttm.url} download={value.rttm.orig_name || value.rttm.path}>
				<IconButton Icon={Download} label={i18n("common.download")} />
			</DownloadLink>
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
	<AudioPlayerWithAnnotation
		value={value}
		{label}
		{i18n}
		{waveform_settings}
		{waveform_options}
		on:pause
		on:play
		on:stop
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
