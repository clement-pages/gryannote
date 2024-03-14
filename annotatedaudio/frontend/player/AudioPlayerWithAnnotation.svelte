<script lang="ts">
	import type { Annotation, WaveformOptions , CaptionLabel} from "../shared/types";
	import type { I18nFormatter } from "@gradio/utils";

	import { onMount } from "svelte";
	import { Music, Undo} from "@gradio/icons";
	import Gum from "../shared/icons/Gum.svelte";
	import WaveSurfer from "wavesurfer.js";
	import RegionsPlugin, {
		type Region
	} from "wavesurfer.js/dist/plugins/regions.js";
	import WaveformControls from "../shared/WaveformControls.svelte";
	import { Empty } from "@gradio/atoms";
	import { resolve_wasm_src } from "@gradio/wasm/svelte";
	import AnnotatedAudioData from "../shared/AnnotatedAudioData";
	import { createEventDispatcher } from "svelte";
	import Caption from "../shared/Caption.svelte"

	export let value: null | AnnotatedAudioData = null;
	$: url = value.file_data?.url;
	export let label: string;
	export let i18n: I18nFormatter;
	export let interactive = true;
	export let editable = true;
	export let waveform_settings: Record<string, any>;
	export let waveform_options: WaveformOptions;
	export let mode = "";

	let container: HTMLDivElement;
	let waveform: WaveSurfer | undefined;
	let wsRegions: RegionsPlugin;
	let activeRegion: Region | null = null;
	let leftRegionHandle: HTMLDivElement | null;
	let rightRegionHandle: HTMLDivElement | null;
	let activeHandle = "";

	let timeRef: HTMLTimeElement;
	let durationRef: HTMLTimeElement;
	let audio_duration: number;
	let playing = false;

	let trimDuration = 0;

	let show_volume_slider = false;
	let showRedo = interactive;

	let initialAnnotations: Annotation[] | null = null;
	// correspondance between a Region and an Annotation
	let regionsMap: Map<string, Annotation> = new Map();

	let defaultLabel: CaptionLabel | null = null;
	let activeLabel: CaptionLabel | null = null;

	const dispatch = createEventDispatcher<{
		stop: undefined;
		play: undefined;
		pause: undefined;
		edit: typeof value;
		end: undefined;
	}>();

	function formatTime(seconds: number): string {
		const minutes = Math.floor(seconds / 60);
		const secondsRemainder = Math.round(seconds) % 60;
		const paddedSeconds = `0${secondsRemainder}`.slice(-2);
		return `${minutes}:${paddedSeconds}`;
	};

	function create_waveform(): void {
		waveform = WaveSurfer.create({
			container: container,
			...waveform_settings
		});
		resolve_wasm_src(value.file_data?.url).then((resolved_src) => {
			if (resolved_src && waveform) {
				return waveform.load(resolved_src);
			}
		});

		waveform.on("dblclick", (_, relativeY) => {
			// allow the user to add a region only after the pipeline has been applied
			if(value?.annotations){
				addAnnotation(relativeY);
			}
		});
	};

	/**
	 * Print annotations on waveform by linking regions to each annotations.
	 * A region can be view as a visual representation of an annotation.
	 */
	function initAnnotations(): void {

		var annotations = value.annotations;

		// keep initial annotations in memory, for future retrieval
		if (initialAnnotations === null){
			initialAnnotations = []
			// Set default label with first annotation's speaker and color
			defaultLabel = {speaker: annotations[0].speaker, color: annotations[0].color, shortcut: "A"};
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
	 * 
	 * @param relativeY
	 */
	function addAnnotation(relativeY: number): void{
		let annotationLabel = (activeLabel !== null ? activeLabel : defaultLabel);
		// if annotations were not initialized, do nothin
		if (annotationLabel === null){
			return;
		}
		let region = wsRegions.addRegion({
			start: relativeY - 1.0,
			end: relativeY + 1.0,
			color: annotationLabel.color,
			drag: true,
			resize: true,
		});
		regionsMap.set(region.id, {
			start: region.start,
			end: region.end, 
			color: region.color, 
			speaker: annotationLabel.speaker
		});

		// set region as active one
		setActiveRegion(region);

		updateAnnotations();
	}

	/**
	 * Remove the annotation linked to the specified region
	 * @param region region of the annotation to be removed
	 */
	function removeAnnotation(region: Region): void {
		regionsMap.delete(region.id)
		region.remove();
		updateAnnotations();
	}

	/**
	 * Reset annotations to their initial state, ie annotations
	 * provided by the pyannote pipeline
	 */
	function resetAnnotations(): void {
		clearAnnotations();
		initialAnnotations.forEach(
				annotation => value.annotations.push(Object.assign({}, annotation))
		);
		initAnnotations();
		console.log(value)
		dispatch("edit", value);
	}

	/**
	 * update annotations with current regions' state
	 */
	function updateAnnotations(): void {
		value.annotations = Array.from(regionsMap.values());
		dispatch("edit", value);
	}

	/**
	 * Clear all the annotations, and linked regions, from the waveform
	 */
	function clearAnnotations(): void {
		wsRegions?.clearRegions();
		value.annotations = []
		regionsMap.clear()
	};

	/**
	 * Set active region with specified region.
	 * @param region the region to activate
	 */
	function setActiveRegion(region: Region): void {
		if(activeRegion !== null){
			activeRegion.element.style.background = activeRegion.color;
		}
	
		if(region === null){
			activeRegion = region;
			return;
		}
		activeRegion = region;
		activeRegion.element.style.background = "repeating-linear-gradient(45deg,"
						+ region.color
						+ " ,"
						+ region.color
						+ " 10px, #ffffff 10px ,#ffffff 15px)";
	}

	/**
	 * Set annotation speaker for the active annotation with specified
	 * speaker label
	 * @param activeCaptionLabel active caption's label
	 */
	function setAnnotationSpeaker(activeCaptionLabel: CaptionLabel){
		activeLabel = activeCaptionLabel
		// get label color
		let color = value.annotations.find((annotation) => annotation.speaker === activeLabel.speaker).color;
		// if label does not exist
		if (color === undefined){
			return;
		}

		if(activeRegion !== null) {
			activeRegion.color = color;
			activeRegion.setOptions({
				start: activeRegion.start,
				end: activeRegion.end,
				color: color,
				drag: true,
				resize: true,
			});
			let activeAnnotation = regionsMap.get(activeRegion.id);
			activeAnnotation.color = color;
			activeAnnotation.speaker = activeLabel.speaker;
			updateAnnotations();
		}
	}

	/**
	 * Select the annotation next (in terms of time) to current
	 * active annotation. If active annotation is the last one,
	 * the next region to be activated is the first annotation
	 * on the waveform.
	 * @param shiftPressed: go ahead if true, else go back
	 */
	function selectNextAnnotation(shiftPressed: boolean): void {
		// go back if shift was pressed, else go ahead:
		var direction = shiftPressed ? -1 : 1;
		var regions = wsRegions.getRegions().sort((r1, r2) => r1.start > r2.start ? 1 : -1);
		// if there is no active region, active the first one
		if(activeRegion === null){
			setActiveRegion(regions[0]);
		}
		else{
			var activeRegionIdx = regions.indexOf(activeRegion);
			setActiveRegion(regions.at((activeRegionIdx + direction) % regions.length));
		}
	};

	function adjustRegionHandles(handle: string, key: string): void {
		let newStart: number;
		let newEnd: number;

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

	$: if (container !== undefined) {
		if (waveform !== undefined) waveform.destroy();
		container.innerHTML = "";
		create_waveform();
		playing = false;
	}

	$: if(waveform){
		wsRegions = waveform.registerPlugin(RegionsPlugin.create());
	}

	$: if(value?.annotations !== null && initialAnnotations === null){
		initAnnotations();
	}

	$: waveform?.on("decode", (duration: any) => {
		audio_duration = duration;
		durationRef && (durationRef.textContent = formatTime(duration));
	});

	$: waveform?.on(
		"timeupdate",
		(currentTime: any) =>
			timeRef && (timeRef.textContent = formatTime(currentTime))
	);

	$: waveform?.on("ready", () => {
		if (!waveform_settings.autoplay) {
			waveform?.stop();
		} else {
			waveform?.play();
		}
	});

	$: waveform?.on("finish", () => {
		playing = false;
		dispatch("stop");
	});

	$: waveform?.on("pause", () => {
		playing = false;
		dispatch("pause");
	});

	$: waveform?.on("play", () => {
		playing = true;
		dispatch("play");
	});

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
			setActiveRegion(region);
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

	async function load_audio(data: string): Promise<void> {
		await resolve_wasm_src(data).then((resolved_src) => {
			if (!resolved_src || value.file_data?.is_stream) return;
			return waveform?.load(resolved_src);
		});
	}

	$: url && load_audio(url);

	onMount(() => {
		window.addEventListener("keydown", (e) => {
			switch(e.key){
				case "ArrowLeft":  adjustRegionHandles(activeHandle, "ArrowLeft"); break;
				case "ArrowRight": adjustRegionHandles(activeHandle, "ArrowRight"); break;
				case "Escape": setActiveRegion(null); break;
				case "Tab": e.preventDefault(); selectNextAnnotation(e.shiftKey); break;
				case "Enter": e.preventDefault(); addAnnotation(waveform.getCurrentTime()); break;
				default: //do nothing
			}
		});
	});
</script>

{#if value === null}
	<Empty size="small">
		<Music />
	</Empty>
{:else if value.file_data.is_stream}
	<audio
		class="standard-player"
		src={value.file_data.url}
		controls
		autoplay={waveform_settings.autoplay}
	/>
{:else}
	<div
		class="component-wrapper"
		data-testid={label ? "waveform-" + label : "unlabelled-audio"}
	>
		<div class="waveform-container">
			<div id="waveform" bind:this={container} />
		</div>

		<div class="timestamps">
			<time bind:this={timeRef} id="time">0:00</time>
			<div>
				{#if mode === "edit" && trimDuration > 0}
					<time id="trim-duration">{formatTime(trimDuration)}</time>
				{/if}
				<time bind:this={durationRef} id="duration">0:00</time>
			</div>
		</div>

		{#if waveform}
			<div class="commands">
				<div class="waveform-controls">
					<WaveformControls
						{waveform}
						{playing}
						{audio_duration}
						{i18n}
						bind:show_volume_slider
						{waveform_options}
					/>
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
			{#if value?.annotations}
				<Caption
					value={value.annotations}
					on:select={(e) => setAnnotationSpeaker(e.detail)}
				/>
			{/if}
		{/if}
	</div>
{/if}

<style>
	.action {
		width: var(--size-5);
		width: var(--size-5);
		color: var(--neutral-400);
		margin-left: var(--spacing-md);
	}

	.annotations-actions {
		display: flex;
		justify-self: self-end;
		align-items: center;
	}

	.commands {
		display: flex;
		justify-content: space-between;
	}

	.component-wrapper {
		padding: 4em;
	}

	.icon:hover {
		color: var(--color-accent);
	}

	.remove-button {
		fill: #9ca3af;
	}

	.remove-button:hover, .remove-button:focus {
		fill: var(--color-accent);
	}

	:global(::part(wrapper)) {
		margin-bottom: var(--size-2);
	}

	.timestamps {
		display: flex;
		justify-content: space-between;
		align-items: center;
		width: 100%;
		padding: var(--size-1) 0;
	}

	#time {
		color: var(--neutral-400);
	}

	#duration {
		color: var(--neutral-400);
	}

	#trim-duration {
		color: var(--color-accent);
		margin-right: var(--spacing-sm);
	}
	.waveform-container {
		display: flex;
		align-items: center;
		justify-content: center;
		width: var(--size-full);
	}

	.waveform-controls {
		width: 80em;
	}

	#waveform {
		width: 100%;
		height: 100%;
		position: relative;
	}

	.standard-player {
		width: 100%;
		padding: var(--size-2);
	}
</style>
