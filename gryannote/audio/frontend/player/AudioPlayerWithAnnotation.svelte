<script lang="ts">
	import type { Annotation, WaveformOptions , CaptionLabel} from "../shared/types";
	import type { I18nFormatter } from "@gradio/utils";

	import { onMount } from "svelte";
	import { Music, Undo, Trim } from "@gradio/icons";
	import Gum from "../shared/icons/Gum.svelte";
	import WaveSurfer from "wavesurfer.js";
	import RegionsPlugin, {
		type Region,
		type RegionParams,
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

	let show_volume_slider = false;
	let showRedo = interactive;
	// keep initial annotations in memory
	let initialAnnotations: Annotation[] | null = null;
	// correspondence between a Region and an Annotation
	let regionsMap: Map<string, Annotation> = new Map();

	let caption: Caption;
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

		waveform.on("dblclick", () => {
			handleRegionAdd(waveform.getCurrentTime());
		});
	};

	/**
	 * Print regions on waveform given annotation data provided by the pipeline.
	 * A region can be view as a visual representation of an annotation.
	 */
	function createRegions(annotations: Annotation[]): void {

		if (!initialAnnotations){
			initialAnnotations = [...annotations];
		}
		if(annotations.length === 0){
			return;
		}

		const currentAnnotations = Array.from(regionsMap.values());
		annotations = annotations.filter(annotation => !currentAnnotations.some(currentAnnotation =>
			annotation.start === currentAnnotation.start &&
			annotation.end === currentAnnotation.end &&
			annotation.speaker === currentAnnotation.speaker
		))

		annotations.forEach(annotation => {
			let label = caption.createLabel(annotation.speaker)
			let region = addRegion({
				start: annotation.start,
				end: annotation.end,
				color: label.color,
				drag: true,
				resize: true,
			}, annotation.speaker);
			region.element.style.top = (annotation.level * 10).toString() + "%";
			region.element.style.height = (100 - (annotation.numLevels + 1) * 10 ).toString() + "%";

		});
	}

	/**
	 * update annotations with current regions' state
	 */
	 function updateAnnotations(): void {
		value.annotations = Array.from(regionsMap.values());
		dispatch("edit", value);
	}


	/**
	 * Add a region on the waveform given its parameters and speaker label
	 * @param options region's params (start, end, color)
	 * @param speaker region's label
	 *
	 * @returns the added region
	 */
	function addRegion(options: RegionParams, speaker: string): Region {
		let region = wsRegions.addRegion(options);
		const annotation = {start: region.start, end: region.end, speaker: speaker, color: region.color};
		regionsMap.set(region.id, annotation);

		// if this is the first region added on the waveform
		if(!initialAnnotations){
			initialAnnotations = [annotation];
		}
		updateAnnotations();

		return region;
	}

	/**
	 * Handle add region event. The new added region become the active region.
	 * @param relativeY mouse y-coordinate relative to waveform start
	 */
	function handleRegionAdd(relativeY: number): void{
		let label = (activeLabel ? activeLabel : defaultLabel);
		// if annotations were not initialized, do nothing
		if (!label){
			label = caption.createLabel();
		}
		let region = addRegion({
			start: relativeY - 1.0,
			end: relativeY + 1.0,
			color: label.color,
			drag: true,
			resize: true,
		}, label.speaker);

		// set region as active one
		setActiveRegion(region);
	}

	/**
	 * Remove specified region from waveform as well as
	 * the linked annotation
	 * @param region region to remove
	 */
	function removeRegion(region: Region): void {
		// if region to remove is the active one, first unselect it:
		if(region === activeRegion){
			setActiveRegion(null);
		}
		regionsMap.delete(region.id)
		region.remove();
		updateAnnotations();
	}

	/**
	 * Handle the region removal event, and remove the active region. According to `key` and
	 * `shiftKey` value, the new active region is the one set before or after the removed region.
	 * Do nothing if there is no active region.
	 * @param key shortcut name. Help to determine which region to select after the removal.
	 * @param shiftKey indicates whether shift key was pressed. Help to determine which region to select
	 */
	function handleRegionRemoval(key: string, shiftKey: boolean): void {
		// if there is no active region, do nothing
		if(!activeRegion){
			return;
		}

		let region2remove = wsRegions.getRegions().find((region) => region.id === activeRegion.id);
		// remove active region and set the next region as the active one
		if(key === "Delete" || (key == "Backspace" && shiftKey)){
			selectNextRegion(false);
		}
		// remove region and set the previous region as the active one
		else {
			selectNextRegion(true);
		}

		removeRegion(region2remove);
	}

	/**
	 * Reset regions to their initial state, ie from annotations
	 * data provided by pipeline
	 */
	function resetRegions(): void {
		clearRegions();
		initialAnnotations.forEach(
				annotation => value.annotations.push(Object.assign({}, annotation))
		);
		createRegions(value.annotations);
		dispatch("edit", value);
	}

	/**
	 * Clear all the regions from waveform, as well as
	 * annotation data given by pipeline
	 */
	function clearRegions(): void {
		setActiveRegion(null);
		wsRegions?.clearRegions();
		value.annotations = [];
		regionsMap.clear();
	};

	/**
	 * Set active region with specified one.
	 * @param region the region to activate
	 */
	function setActiveRegion(region: Region): void {
		if(activeRegion){
			activeRegion.element.style.background = activeRegion.color;
		}

		activeRegion = region;
		if(!activeRegion){
			return;
		}

		activeRegion.element.style.background = "repeating-linear-gradient(45deg,"
						+ region.color
						+ " ,"
						+ region.color
						+ " 10px, #ffffff 10px ,#ffffff 15px)";
	}

	/**
	 * Set region speaker for the active region with specified
	 * speaker label
	 * @param label active caption's label
	 */
	function setRegionSpeaker(label: CaptionLabel){
		// get label color

		if(activeRegion !== null) {
			// update region color
			activeRegion.setOptions({
				start: activeRegion.start,
				end: activeRegion.end,
				color: label.color,
				drag: true,
				resize: true,
			});
			activeRegion.element.style.background = "repeating-linear-gradient(45deg,"
						+ activeRegion.color
						+ " ,"
						+ activeRegion.color
						+ " 10px, #ffffff 10px ,#ffffff 15px)";

			// update corresponding annotation color
			let activeAnnotation = regionsMap.get(activeRegion.id);
			activeAnnotation.speaker = label.speaker;
			updateAnnotations();
		}
	}

	/**
	 * Select the region next (in terms of time) to the current
	 * active one. If active region is the last one,
	 * the next region to be activated is the first one
	 * on the waveform.
	 * @param shiftKey: go back if true, go ahead otherwise
	 */
	function selectNextRegion(shiftKey: boolean): void {
		// go back if shift was pressed, else go ahead:
		var direction = shiftKey ? -1 : 1;
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

	/**
	 * Split the specified region at indicated split time, and set
	 * active region to the resulting right region.
	 * @param region region to split
	 * @param splitTime split position. Must be inside region's boundaries
	 */
	function splitRegion(region: Region, splitTime: number){
		if (splitTime < region.start || splitTime > region.end){
			throw new RangeError("split time out of region bounds");
		}

		let speaker = regionsMap.get(region.id).speaker;

		let regionLeft = addRegion({
			start: region.start,
			end: splitTime,
			color: region.color,
			drag: region.drag,
			resize: region.resize,
		}, speaker);

		let regionRight = addRegion({
			start: splitTime,
			end: region.end,
			color: region.color,
			drag: region.drag,
			resize: region.resize,
		}, speaker);

		// update active region
		setActiveRegion(regionRight);
		// remove split region
		removeRegion(region);

	}

	/**
	 * Split a region into two distinct regions. There are two cases (sorted by priority):
	 * - if there is an active region, split this region
	 * - else, split the region in which the time cursor is
	 * - if the cursor is out on any region, do nothing
	 * @param currentTime position of the cursor on the waveform
	 */
	function handleRegionSplit(currentTime: number): void {
		// get region in which the cursor in currently located
		let region = wsRegions.getRegions().find(
			(_region) => _region.start < currentTime && _region.end > currentTime
		);
		if(region === undefined){
			// if cursor is not in a region, use active region, if available
			if(activeRegion === null){
				return;
			}
			region = activeRegion;
			currentTime = region.start + (region.end - region.start) / 2.;
		}
		splitRegion(region, currentTime);
	}

	/**
	 * Adjust region start and end time bounds
	 * @param key shortcut name. Indicates direction: forward or backward.
	 * @param shiftKey indicates whether shift key was pressed. If true, move faster
	 * @param altKey indicates whether alt key was pressed. If true, move end bound,
	 * else start bound
	 */
	function adjustRegionBounds(key: string, shiftKey: boolean, altKey: boolean): void {
		let newStart: number;
		let newEnd: number;
		let delta: number = 0.05; //TODO do not hardcore this and adapt it according to relative size of the waveform

		// if alt is pressed, go faster
		if(shiftKey){
			delta = delta * 4.0;
		}

		// edit active region end time
		if (!altKey) {
			if (key === "ArrowLeft") {
				newStart = activeRegion.start - delta;
				newEnd = activeRegion.end;
			} else {
				newStart = activeRegion.start + delta;
				newEnd = activeRegion.end;
			}
		// edit active region start time
		} else {
			if (key === "ArrowLeft") {
				newStart = activeRegion.start;
				newEnd = activeRegion.end - delta;
			} else {
				newStart = activeRegion.start;
				newEnd = activeRegion.end + delta;
			}
		}

		// saturate region bound
		if(newStart > activeRegion.end){
			newStart = activeRegion.end - 0.1;
		}
		if(newEnd < activeRegion.start){
			newEnd = activeRegion.start + 0.1;
		}

		activeRegion.setOptions({
			start: newStart,
			end: newEnd
		});
	};

	/**
	 * Adjust position of the cursor on the waveform
	 * @param key shortcut name. Indicates direction: forward or backward.
	 * @param shiftKey indicates whether shift key was pressed. If true, move faster
	 */
	function adjustTimeCursorPosition(key: string, shiftKey: boolean): void {
		let currentTime = waveform.getCurrentTime();
		let newTime: number;
		let delta = 0.05; //TODO do not hardcore this and adapt it according to relative size of the waveform

		// if alt is pressed, go faster
		if(shiftKey){
			delta = delta * 4.0;
		}

		if(key === "ArrowLeft"){
			newTime = currentTime - delta;
		}else {
			newTime = currentTime + delta;
		}

		waveform.setTime(newTime);
	}

	/**
	 * Handle time adjustment shortcuts. There are two cases whether there is
	 * an active region set. If yes, region bounds are adjusted. Otherwise, time
	 * cursor position is updated.
	 * @param key shortcut name. Indicates direction: forward or backward.
	 * @param shiftKey indicates whether shift key was pressed. If true, move faster
	 * @param altKey indicates whether alt key was pressed. If true, move end bound,
	 * else start bound. No effect when updating time cursor.
	 */
	function handleTimeAdjustement(key: string, shiftKey: boolean, altKey: boolean): void {
		// if there is an active region, update region bounds
		if(activeRegion){
			adjustRegionBounds(key, shiftKey, altKey);
			return;
		}
		// else update time cursor position
		adjustTimeCursorPosition(key, shiftKey);
	}

	$: if (container !== undefined) {
		if (waveform !== undefined) waveform.destroy();
		container.innerHTML = "";
		create_waveform();
		playing = false;
	}

	$: if(value?.annotations !== null && wsRegions){
		createRegions(value.annotations);
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
		if(wsRegions === undefined ){
			wsRegions = waveform.registerPlugin(RegionsPlugin.create());

			// add region-clicked event listener
			wsRegions?.on("region-clicked", (region, e) => {
				switch(mode){
					case "remove": removeRegion(region); break;
					case "split": splitRegion(region, region.start + (region.end - region.start) / 2); break;
					default: setActiveRegion(region); region.play();
				}
				mode = "";
			});

			wsRegions?.on("region-updated", (region) => {
				var updatedAnnotation = regionsMap.get(region.id);
				updatedAnnotation.start = region.start;
				updatedAnnotation.end = region.end;
				updateAnnotations();
			});
		}
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
				case "ArrowLeft": handleTimeAdjustement("ArrowLeft", e.shiftKey, e.altKey); break;
				case "ArrowRight": handleTimeAdjustement("ArrowRight", e.shiftKey, e.altKey); break;
				case "Escape": setActiveRegion(null); break;
				case "Tab": e.preventDefault(); selectNextRegion(e.shiftKey); break;
				case "Delete": handleRegionRemoval("Delete", e.shiftKey); break;
				case "Backspace": handleRegionRemoval("Backspace", e.shiftKey); break;
				case "Enter":
					e.preventDefault();
					if(e.shiftKey){
						handleRegionSplit(waveform.getCurrentTime());
					} else {
						handleRegionAdd(waveform.getCurrentTime());
					}
					break;
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
				<div class="regions-actions">
					{#if editable && interactive && value}
					{#if showRedo}
						<button
							class="action icon"
							aria-label="Reset annotations"
							title={i18n("Reset annotations")}
							on:click={resetRegions}
						>
							<Undo/>
						</button>
					{/if}
					<button
						class="action icon remove-button"
						aria-label="Remove an annotation"
						title={i18n("Remove an annotation")}
						on:click={() => mode = "remove"}
					>
						<Gum/>
					</button>
					<button
						class="action icon trim-button"
						aria-label="Split an annotation"
						title={i18n("Split an annotation")}
						on:click={() => mode = "split"}
					>
						<Trim/>
					</button>
				{/if}
				</div>
			</div>
			{#if value}
				<Caption
					bind:this={caption}
					bind:defaultLabel
					bind:activeLabel
					on:select={(e) => setRegionSpeaker(e.detail)}
					on:select={(e) => activeLabel = e.detail}
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

	.regions-actions {
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

	.remove-button, .trim-button {
		fill: var(--neutral-400);
	}

	.remove-button:hover, .remove-button:focus {
		fill: var(--color-accent);
	}

	.trim-button:hover, .trim-button:focus {
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
