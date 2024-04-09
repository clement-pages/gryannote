<script lang="ts">
	import { Play, Pause, Forward, Backward} from "@gradio/icons";
	import Magnifier from "./icons/Magnifier.svelte";
	import { get_skip_rewind_amount } from "../shared/utils";
	import type { I18nFormatter } from "@gradio/utils";
	import WaveSurfer from "wavesurfer.js";
	import type {WaveformOptions } from "./types";
	import VolumeLevels from "./VolumeLevels.svelte";
	import VolumeControl from "./VolumeControl.svelte";
	import { onMount } from "svelte";

	export let waveform: WaveSurfer;
	export let audio_duration: number;
	export let i18n: I18nFormatter;
	export let playing: boolean;
	export let waveform_options: WaveformOptions = {};
	export let show_volume_slider = false;
	export let showZoomSlider = false;

	let playbackSpeeds = [0.5, 1, 1.5, 2];
	let playbackSpeed = playbackSpeeds[1];

	let currentVolume = 1;

	let currentZoom: number = 10;
	let zoomMin: number = 10;
	let zoomMax: number = 10000;
	let zoomDelta = 100;

	/**
	 * Update zoom value
	 * @param zoom new value for zoom
	 */
	function updateZoom(zoom: number): void{
		currentZoom = zoom;
		if(currentZoom < zoomMin){
			currentZoom = zoomMin;
		}
		else if(currentZoom > zoomMax){
			currentZoom = zoomMax;
		}
		waveform.zoom(currentZoom);
	}

	onMount(() => {
		window.addEventListener("keydown", (e) =>{
			switch(e.key){
				case " ": waveform.playPause(); e.preventDefault(); break;
				case "ArrowUp": e.preventDefault(); updateZoom(currentZoom + zoomDelta); break;
				case "ArrowDown": e.preventDefault(); updateZoom(currentZoom - zoomDelta); break;
				default: //do nothing
			}
		})
	});

</script>

<div class="controls" data-testid="waveform-controls">
	<div class="control-wrapper">
		<button
			class="action icon volume"
			aria-label="Adjust volume"
			on:click={() => (show_volume_slider = !show_volume_slider)}
		>
			<VolumeLevels {currentVolume} />
		</button>

		{#if show_volume_slider}
			<VolumeControl bind:currentVolume bind:show_volume_slider {waveform} />
		{/if}

		<button
			class:hidden={show_volume_slider}
			class="playback icon"
			aria-label={`Adjust playback speed to ${
				playbackSpeeds[
					(playbackSpeeds.indexOf(playbackSpeed) + 1) % playbackSpeeds.length
				]
			}x`}
			on:click={() => {
				playbackSpeed =
					playbackSpeeds[
						(playbackSpeeds.indexOf(playbackSpeed) + 1) % playbackSpeeds.length
					];

				waveform.setPlaybackRate(playbackSpeed);
			}}
		>
			<span>{playbackSpeed}x</span>
		</button>
		<div class="zoom-wrapper">
			<button
			class="zoom-button icon"
				on:click={() => showZoomSlider = !	showZoomSlider}
			>
				<Magnifier/>
			</button>
			{#if showZoomSlider}
				<input
					type="range"
					min={zoomMin}
					max={zoomMax}
					bind:value={currentZoom}
					on:input={(e) => updateZoom(e.target.value)}
					on:focusout={() => showZoomSlider = false}
				>
				{/if}
		</div>
	</div>

	<div class="play-pause-wrapper">
		<button
			class="rewind icon"
			aria-label={`Skip backwards by ${get_skip_rewind_amount(
				audio_duration,
				waveform_options.skip_length
			)} seconds`}
			on:click={() =>
				waveform.skip(
					get_skip_rewind_amount(audio_duration, waveform_options.skip_length) *
						-1
				)}
		>
			<Backward />
		</button>
		<button
			class="play-pause-button icon"
			on:click={() => waveform.playPause()}
			aria-label={playing ? i18n("audio.pause") : i18n("audio.play")}
		>
			{#if playing}
				<Pause />
			{:else}
				<Play />
			{/if}
		</button>
		<button
			class="skip icon"
			aria-label="Skip forward by {get_skip_rewind_amount(
				audio_duration,
				waveform_options.skip_length
			)} seconds"
			on:click={() =>
				waveform.skip(
					get_skip_rewind_amount(audio_duration, waveform_options.skip_length)
				)}
		>
			<Forward />
		</button>
	</div>
</div>

<style>

	.controls {
		display: grid;
		grid-template-columns: 1fr 1fr 1fr;
		margin-top: 5px;
		align-items: center;
		position: relative;
	}

	.hidden {
		display: none;
	}

	.control-wrapper {
		display: flex;
		justify-self: self-start;
		align-items: center;
		justify-content: space-between;
	}

	@media (max-width: 375px) {
		.controls {
			display: flex;
			flex-wrap: wrap;
		}

		.controls * {
			margin: var(--spacing-sm);
		}

	}

	.action {
		width: var(--size-5);
		width: var(--size-5);
		color: var(--neutral-400);
		margin-left: var(--spacing-md);
	}
	.icon:hover {
		color: var(--color-accent);
		fill: var(--color-accent);
	}
	.play-pause-wrapper {
		display: flex;
		justify-self: right;
	}
	.playback {
		border: 1px solid var(--neutral-400);
		border-radius: var(--radius-sm);
		width: 5.5ch;
		font-weight: 300;
		font-size: var(--size-3);
		text-align: center;
		color: var(--neutral-400);
		height: var(--size-5);
		font-weight: bold;
	}

	.playback:hover,
	.playback:focus {
		color: var(--color-accent);
		border-color: var(--color-accent);
	}

	.rewind,
	.skip {
		margin: 0 10px;
		color: var(--neutral-400);
	}

	.play-pause-button {
		width: var(--size-8);
		width: var(--size-8);
		display: flex;
		align-items: center;
		justify-content: center;
		color: var(--neutral-400);
		fill: var(--neutral-400);
	}

	.volume {
		position: relative;
		display: flex;
		justify-content: center;
		margin-right: var(--spacing-xl);
	}

	.zoom-button {
		width: 1.75em;
		fill: var(--neutral-400);
	}
</style>
