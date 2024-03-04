<script lang="ts">
	import { Play, Pause, Forward, Backward, Undo } from "@gradio/icons";
	import Gum from "./icons/Gum.svelte";
	import { get_skip_rewind_amount } from "../shared/utils";
	import type { I18nFormatter } from "@gradio/utils";
	import type { Annotation } from "./types";
	import WaveSurfer from "wavesurfer.js";
	import RegionsPlugin, {
		type Region
	} from "wavesurfer.js/dist/plugins/regions.js";
	import type {WaveformOptions } from "./types";
	import AnnotatedAudioData from "./AnnotatedAudioData";
	import VolumeLevels from "./VolumeLevels.svelte";
	import VolumeControl from "./VolumeControl.svelte";
	import { createEventDispatcher } from "svelte";

	export let value: AnnotatedAudioData | null = null;
	export let waveform: WaveSurfer;
	export let audio_duration: number;
	export let i18n: I18nFormatter;
	export let playing: boolean;
	export let showRedo = false;
	export let interactive = false;
	export let mode = "";
	export let container: HTMLDivElement;
	export let waveform_options: WaveformOptions = {};
	export let show_volume_slider = false;
	export let editable = true;

	export let trimDuration = 0;

	let initialAnnotations: Annotation[]  = [];

	let playbackSpeeds = [0.5, 1, 1.5, 2];
	let playbackSpeed = playbackSpeeds[1];

	let wsRegions: RegionsPlugin;
	let activeRegion: Region | null = null;

	let leftRegionHandle: HTMLDivElement | null;
	let rightRegionHandle: HTMLDivElement | null;
	let activeHandle = "";

	// correspondance between a SingleRegion and an Annotation
	let regionsMap : Map<string, Annotation> = new Map();

	let currentVolume = 1;

	const dispatch = createEventDispatcher<{
		edit: typeof value;
	}>();

	$: wsRegions = waveform.registerPlugin(RegionsPlugin.create());

	$: if(value?.annotations !== null && initialAnnotations.length === 0){
		addAnnotations()
	}

	$: wsRegions?.on("region-updated", (region) => {
		var updatedAnnotation = regionsMap.get(region.id);
		updatedAnnotation.start = region.start;
		updatedAnnotation.end = region.end;
		updateAnnotations();
	});

	$: wsRegions?.on("region-clicked", (region, e) => {
		e.stopPropagation(); // prevent triggering a click on the waveform
		// if removal mode is enable, remove clicked region
		if (region && mode === "remove") {
			removeAnnotation(region)
		}
		else{
			// update the active region
			if(activeRegion !== null) {
				activeRegion.element.classList.remove("active-region");
			}
			activeRegion = region;
			console.log(activeRegion.id);
			activeRegion.element.classList.add("active-region");
			region.play();
		}
	});

	$: if (activeRegion) {
		const shadowRoot = container.children[0]!.shadowRoot!;

		rightRegionHandle = shadowRoot.querySelector('[data-resize="right"]');
		leftRegionHandle = shadowRoot.querySelector('[data-resize="left"]');

		if (leftRegionHandle && rightRegionHandle) {
			leftRegionHandle.setAttribute("role", "button");
			rightRegionHandle.setAttribute("role", "button");
			leftRegionHandle?.setAttribute("aria-label", "Drag to adjust start time");
			rightRegionHandle?.setAttribute("aria-label", "Drag to adjust end time");
			leftRegionHandle?.setAttribute("tabindex", "0");
			rightRegionHandle?.setAttribute("tabindex", "0");

			leftRegionHandle.addEventListener("focus", () => {
				if (wsRegions) activeHandle = "left";
			});

			rightRegionHandle.addEventListener("focus", () => {
				if (wsRegions) activeHandle = "right";
			});
		}
	}

	/**
	 * Print annotations on waveform by linking regions to each annotations.
	 * A region can be view as a visual representation of an annotation.
	 */
	const  addAnnotations = (): void =>{

		var annotations = value.annotations;

		// keep initial annotations in memory, for future retrieval
		if (initialAnnotations.length == 0){
			annotations.forEach(
				annotation => initialAnnotations.push(Object.assign({}, annotation))
			);
		}

		value.annotations.forEach(annotation => {
			var region = wsRegions.addRegion({
				start: annotation.start,
				end: annotation.end,
				color: annotation.color,
				drag: true,
				resize: true,
			})
			region.element.style.top = (annotation.level * 10).toString() + "%";
			region.element.style.height = (100 - (annotation.numLevels + 1) * 10 ).toString() + "%";

			// link annotation to region
			regionsMap.set(region.id, annotation);

		});
	}

	/**
	 * Remove the annotation linked to the specified region
	 * @param region region of the annotation to be removed
	 */
	const removeAnnotation = (region: Region): void => {
		regionsMap.delete(region.id)
		region.remove();
		updateAnnotations();
	}

	/**
	 * Reset annotations to their initial state, ie annotations
	 * provided by the pyannote pipeline
	 */
	const resetAnnotations = (): void  => {
		clearAnnotations();
		initialAnnotations.forEach(
				annotation => value.annotations.push(Object.assign({}, annotation))
		);
		addAnnotations();
		console.log(value)
		dispatch("edit", value);
	}

	/**
	 * update annotations with current regions' state
	 */
	const updateAnnotations = (): void => {
		value.annotations = Array.from(regionsMap.values());
		dispatch("edit", value);
	}

	/**
	 * Clear all the annotations, and linked regions, from the waveform
	 */
	const clearAnnotations = (): void => {
		wsRegions?.clearRegions();
		value.annotations = []
		regionsMap.clear()
	};

	/**
	 * Select the annotation next (in terms of time) to current
	 * active annotation. If active annotation is the last one,
	 * the next region to be activated is the first annotation
	 * on the waveform.
	 */
	const selectNextAnnotation = (shiftPressed: boolean): void => {
		if(activeRegion !== null){
			// do nothing if there is no active annotation
			return;
		}

		// Go back if shift was pressed, else go ahead:
		var direction = shiftPressed ? -1 : 1;
		var regions = wsRegions.getRegions();
		console.log(regions);
		var activeRegionIdx = regions.indexOf(activeRegion);
		activeRegion = regions.at((activeRegionIdx + direction) % regions.length);
		console.log(activeRegion.id);
	};

	const adjustRegionHandles = (handle: string, key: string): void => {
		let newStart;
		let newEnd;

		if (!activeRegion) return;
		if (handle === "left") {
			if (key === "ArrowLeft") {
				newStart = activeRegion.start - 0.05;
				newEnd = activeRegion.end;
			} else {
				newStart = activeRegion.start + 0.05;
				newEnd = activeRegion.end;
			}
		} else {
			if (key === "ArrowLeft") {
				newStart = activeRegion.start;
				newEnd = activeRegion.end - 0.05;
			} else {
				newStart = activeRegion.start;
				newEnd = activeRegion.end + 0.05;
			}
		}

		activeRegion.setOptions({
			start: newStart,
			end: newEnd
		});

		trimDuration = activeRegion.end - activeRegion.start;
	};

	waveform?.on("ready", function(){
		wsRegions.clearRegions();
		window.addEventListener("keydown", (e) => {
			switch(e.key){
				case "ArrowLeft": adjustRegionHandles(activeHandle, "ArrowLeft"); break;
				case "ArrowRight": adjustRegionHandles(activeHandle, "ArrowRight"); break;
				case "Tab": selectNextAnnotation(e.shiftKey); break;
				default: //do nothing
			}
		});
	});

</script>

<div class="controls" data-testid="waveform-controls">
	<div class="control-wrapper">
		<button
			class="action icon volume"
			style:color={show_volume_slider
				? "var(--color-accent)"
				: "var(--neutral-400)"}
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

	<div class="annotations-actions">
		{#if editable && interactive && value.annotations}
			{#if showRedo}
				<button
					class="action icon"
					aria-label="Reset annotations"
					title={i18n("Reset annotations")}
					on:click={resetAnnotations}
				>
					<Undo/>
				</button>
			{/if}
			<button
				class="action icon remove-button"
				aria-label="Remove an annotation"
				title={i18n("Remove an annotation")}
				on:focusin={() => mode = "remove"}
				on:focusout={() => mode = ""}
			>
				<Gum/>
			</button>
		{/if}
	</div>
</div>

<style>
	.annotations-actions {
		display: flex;
		justify-self: self-end;
		align-items: center;
	}

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
	}
	.play-pause-wrapper {
		display: flex;
		justify-self: center;
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

	.remove-button {
		fill: #9ca3af;
	}

	.remove-button:hover, .remove-button:focus {
		fill: var(--color-accent);
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

	::part(region-handle-left){
		border-right-width: 4px !important;
        border-right-color: #fff000 !important;
	}
</style>
