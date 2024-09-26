<script lang="ts">
    import WaveSurfer from "wavesurfer.js";
    import { createEventDispatcher, onMount} from "svelte"
    import RegionsPlugin, { type Region, type RegionParams } from "wavesurfer.js/dist/plugins/regions";
    import { Trim, Undo } from "@gradio/icons";
	import type { I18nFormatter } from "@gradio/utils";
    import AnnotatedAudioData from "./AnnotatedAudioData";
    import type { Annotation, Label } from "./types";
    import Gum from "./icons/Gum.svelte";
    import GamepadPlugin, { type ButtonEvent, type AxeEvent } from "wavesurfer.js/dist/plugins/gamepad";
    import Caption from "./Caption.svelte";

	export let adjustTimeCursorPosition: (string, boolean) => void;
	export let i18n: I18nFormatter;
	export let waveform: WaveSurfer;
	export let wsGamepad: GamepadPlugin;
    export let value: null | AnnotatedAudioData = null;
    export let interactive = true;
    export let isDialogOpen: boolean = false;
	export let caption: Caption;
	export let mode = "";
	export let activeRegion: Region | null = null;

	let container: HTMLDivElement;

	let wsRegions: RegionsPlugin;

    let leftRegionHandle: HTMLDivElement | null = null;
    let rightRegionHandle: HTMLDivElement | null = null;
    let activeHandle = "";

    let initialAnnotations: Annotation[] | null = null;
    // correspondence between a Region and an Annotation
    let regionsMap: Map<string, Annotation> = new Map();

    const dispatch = createEventDispatcher<{
		edit: typeof value;
	}>();

	/**
	 * Set region speaker for the active region with specified
	 * speaker label
	 * @param label active caption's label
	 */
	export function setRegionSpeaker(label: Label){
		// get label color

		if(activeRegion !== null) {
			// update region color
			activeRegion.setOptions({
				start: activeRegion.start,
				end: activeRegion.end,
				color: label.color,
				drag: activeRegion.drag,
				resize: activeRegion.resize,
			});
			setActiveRegionBackground(activeRegion.color);

			// update corresponding annotation color
			let activeAnnotation = regionsMap.get(activeRegion.id);
			activeAnnotation.speaker = label.name;
			updateAnnotations();
		}
	}


    /**
	 * Update active region background with the specified color
	 * @param color new color for the active region
	 */
	export function setActiveRegionBackground(color: string): void{
		if(!activeRegion){
			return;
		}

		activeRegion.element.style.background = (
            "repeating-linear-gradient(45deg,"
			+ color
			+ " ,"
			+ color
			+ " 10px, #ffffff 10px ,#ffffff 15px)"
        );
	}

	/**
	 * Get all created regions
	 */
	export function getRegions(): Region[] {
		return wsRegions.getRegions();
	}

    /**
	 * update annotations with current regions' state and dispatch them to backend
	 */
	function updateAnnotations(): void {
		value.annotations = Array.from(regionsMap.values());
		dispatch("edit", value);
	}

	/**
	 * Return whether specified region is visible on the screen
	 * @param region
	 * @param waveformContainer
	 */
    function isRegionVisible(region: Region, waveformContainer: HTMLElement | string): boolean {
		// Get the left and right boundaries of the waveform view box:
        if(typeof waveformContainer === "string"){
            waveformContainer = document.getElementById(waveformContainer);
        }
		const viewbox = waveformContainer.getBoundingClientRect();
		const viewboxLeft = viewbox.left;
		const viewboxRight = viewbox.right;

		// Get the left and right boundaries of the region
		const regionBox = region.element.getBoundingClientRect();
		const regionBoxLeft = regionBox.left;
		const regionBoxRight = regionBox.right;

		// Check if the region is within the visible bounds of the visible part of the waveform
		const isVisible = (regionBoxLeft >= viewboxLeft && regionBoxRight <= viewboxRight);

    	return isVisible;
	}

    /**
	 * Set active region with specified one.
	 * Do nothing if component is not in interactive mode
	 * @param region the region to activate
	 */
	function setActiveRegion(region: Region): void {
		if(!interactive) return;

		if(activeRegion){
			activeRegion.element.style.background = activeRegion.color;
		}

		activeRegion = region;
		if(!activeRegion){
			return;
		}

		setActiveRegionBackground(region.color);

		// adjust time cursor position so that active region is always visible
		// only update if audio is not playing and active region not visible
		// to prevent audio jumping
		if(!waveform.isPlaying()){
			if(!isRegionVisible(region, container)){
				waveform.setTime(region.start);
			}
		}
	}

    /**
	 * Select the region next (in terms of time) to the current
	 * active one. If active region is the last one,
	 * the next region to be activated is the first one
	 * on the waveform.
	 * @param goBackward: go back if true, go ahead otherwise
	 */
	function selectNextRegion(goBackward: boolean): void {
		// go back if shift was pressed, else go ahead:
		var direction = goBackward ? -1 : 1;
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
	 * Add a region onto waveform given its parameters and speaker label
	 * @param options region's params (start, end, color)
	 * @param label region's label
	 *
	 * @returns the added region
	 */
    function addRegion(options: RegionParams, label: string): Region {
		let region = wsRegions.addRegion(options);
		const annotation = {start: region.start, end: region.end, speaker: label, color: region.color};
		regionsMap.set(region.id, annotation);

		// if this is the first region added on the waveform
		if(!initialAnnotations){
			initialAnnotations = [annotation];
		}
		updateAnnotations();

		return region;
	}

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

		const label = regionsMap.get(region.id).speaker;
		const {start, ...rightRegionOpt} = region
		const regionRight = addRegion({
			start: splitTime,
			...rightRegionOpt,
		}, label);

		const {end, ...leftRegionOpt} = region
		region.setOptions({end: splitTime, ...leftRegionOpt});

		// annotations need to be updated to take into account the split
		onRegionUpdate(region);

		setActiveRegion(regionRight);
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

		regionsMap.delete(region.id);
		region.remove();

		updateAnnotations();
	}

    /**
	 * Adjust region start and end time bounds
	 * @param key shortcut name. Indicates direction: forward or backward.
	 * @param fastMode indicates whether shift key was pressed. If true, move faster
	 * @param side side of the active region to be updated
	 */
    function adjustRegionBounds(key: string, side: "start" | "end", fastMode: boolean): void {
		if(!activeRegion) return;

		//TODO do not hardcore this and adapt it according to relative size of the waveform
		let dx: number = (key === "ArrowLeft" ? -1 : 1);
		if(fastMode){
			dx = dx * 5.0;
		}

		activeRegion._onUpdate(dx, side);
		onRegionUpdate(activeRegion);
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

        // only add new annotations onto waveform
        const currentAnnotations = Array.from(regionsMap.values());
        annotations = annotations.filter(annotation => !currentAnnotations.some(currentAnnotation =>
            annotation.start === currentAnnotation.start &&
            annotation.end === currentAnnotation.end &&
            annotation.speaker === currentAnnotation.speaker
        ))

        annotations.forEach(annotation => {
            let label = caption.createLabel({name: annotation.speaker})
            addRegion({
                start: annotation.start,
                end: annotation.end,
                color: label.color,
                drag: interactive,
                resize: interactive,
            }, annotation.speaker);
        });
    }

	/**
	 * Clear all regions from waveform, as well as
	 * annotation data given by pipeline
	 */
    function clearRegions(): void {
		setActiveRegion(null);
		wsRegions?.clearRegions();
		value.annotations = [];
		regionsMap.clear();
	};

	/**
	 * Reset regions to their initial state, ie to the state contained in
     * initialAnnotations
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
	 * Handle update of the specified region
	 * @param region region to update
	 */
	 function onRegionUpdate(region: Region): void {
		let annotation = regionsMap.get(region.id);
		annotation.start = region.start;
		annotation.end = region.end;
		updateAnnotations();
	}

    /**
	 * Handle region split shortcut event. There are two cases (sorted by priority):
	 * - if there is an active region, split this region
	 * - else, split the region in which the time cursor is
	 * - if the cursor is out on any region, do nothing
	 * Do nothing if the audio component is not in interactive mode.
	 * @param currentTime position of the cursor on the waveform
	 */
	function onRegionSplit(currentTime: number): void {
		if(!interactive) return;

		let region = activeRegion;
		if(region){
			currentTime = region.start + (region.end - region.start) / 2.;
		} else {
			// if no region is activated, select the one on which the time cursor is positioned
			region = wsRegions.getRegions().find(
				(_region) => _region.start < currentTime && _region.end > currentTime
			);
		}

		// if there is not active region and time cursor is not on a region, nothing to do
		if(!region) return;

		splitRegion(region, currentTime);
	}

    /**
	 * Handle add region event. The new added region becomes the active one.
	 * Do nothing if the component is not in interactive mode.
	 * @param relativeY mouse y-coordinate relative to waveform start
	 */
	function handleRegionAdd(relativeY: number): void{
		if(!interactive) return;

		const label = caption.getActiveLabel() || caption.getDefaultLabel();

		let region = addRegion({
			start: relativeY - 1.0,
			end: relativeY + 1.0,
			color: label.color,
			drag: true,
			resize: true,
		}, label.name);

		// set region as active one
		setActiveRegion(region);
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
			const side = (altKey ? "end" : "start");
			adjustRegionBounds(key, side, shiftKey);
			return;
		}
		// else update time cursor position
		adjustTimeCursorPosition(key, shiftKey);
	}


	$: if(value?.annotations !== null && wsRegions){
		createRegions(value.annotations);
	}

	$: waveform.on("init", () => {
		if(container) return;

		let waveformContainer = waveform.options.container
		if(typeof waveformContainer === "string"){
			waveformContainer = document.getElementById(waveformContainer);
		}
		// make a shallow copy of the waveform container
		container = waveformContainer as HTMLDivElement
	});

	function onGamepadButtonPressed(event: ButtonEvent): void  {
		switch(event.idx){
			case 0: setActiveRegion(null); break;
			case 1: handleRegionAdd(waveform.getCurrentTime()); break;
			case 2: handleRegionRemoval("Delete", false); break;
			case 3: onRegionSplit(waveform.getCurrentTime()); break;
			case 4: selectNextRegion(true); break;
			case 5: selectNextRegion(false);break;
			default: // do nothing
		}
	}

	function onGamepadAxePushed(event: AxeEvent): void {
		let direction = event.value < 0? "ArrowLeft" : "ArrowRight";
		switch(event.idx){
			case 0: handleTimeAdjustement(direction, false, false); break;
			case 2: handleTimeAdjustement(direction, false, true); break;
			default: // do nothing
		}
	}

	$: waveform.on("ready", () => {
		if(wsGamepad === undefined){
			wsGamepad = waveform.registerPlugin(GamepadPlugin.create());
			wsGamepad?.on("button-pressed", (e: ButtonEvent) => {
				onGamepadButtonPressed(e);
			});
			wsGamepad?.on("axe-pushed", (e: AxeEvent)=> {
				onGamepadAxePushed(e);
			});
		}

		if(wsRegions === undefined ){
			wsRegions = waveform.registerPlugin(RegionsPlugin.create());
			if(interactive){
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
					onRegionUpdate(region);
				});
			}
		}
	});

	$: waveform.on("dblclick", () => {
			handleRegionAdd(waveform.getCurrentTime());
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

	onMount(() => {
		window.addEventListener("keydown", (e) => {
			// do not process keyboard shortcuts when a dialog popup is open
			if(isDialogOpen) return;
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
						onRegionSplit(waveform.getCurrentTime());
					} else {
						handleRegionAdd(waveform.getCurrentTime());
					}
					break;
				default: //do nothing
			}
		});
	});

</script>

{#if value && waveform}
	<div class="regions-actions">
		{#if interactive}
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
</style>
