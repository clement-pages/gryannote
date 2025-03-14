<script lang="ts">
    import { createEventDispatcher, onMount} from "svelte"
    import { Trim, Undo } from "@gradio/icons";
	import type { I18nFormatter } from "@gradio/utils";
    import AnnotatedAudioData from "../shared/AnnotatedAudioData";
    import type { Annotation, Label } from "../shared/types";
    import Gum from "../shared/icons/Gum.svelte";
	import WaveSurfer from "@gryannote/wavesurfer.js";
	import RegionsPlugin, { type Region, type RegionParams } from "@gryannote/wavesurfer.js/dist/plugins/regions";
    import GamepadPlugin, { type ButtonEvent, type AxeEvent } from "@gryannote/wavesurfer.js/dist/plugins/gamepad";
    import Caption from "./Caption.svelte";

	export let adjustTimeCursorPosition: (s:string, b:boolean) => void;
	export let i18n: I18nFormatter;
	export let waveform: WaveSurfer;
	export let wsRegions: RegionsPlugin;
	export let wsGamepad: GamepadPlugin;
    export let value: null | AnnotatedAudioData = null;
    export let interactive = true;
    export let isDialogOpen: boolean = false;
	export let caption: Caption;
	export let mode = "";

	let container: HTMLDivElement;

    let leftRegionHandle: HTMLDivElement | null = null;
    let rightRegionHandle: HTMLDivElement | null = null;
    let activeHandle = "";

	let activeRegion: Region | null = null;

    let initialAnnotations: Annotation[] | null = null;
    // mapping between a Region and an Annotation
    let regionsMap: Map<string, Annotation> = new Map();

    const dispatch = createEventDispatcher<{
		edit: typeof value;
		"region-in": Region;
		"region-out": Region;
	}>();

	/**
	 * Return label name for the specified region id
	 * @param regionId
	 */
	export function getRegionLabel(regionId: string): string{
		return regionsMap.get(regionId).speaker;
	}

	/**
	 * Set the specified region's label with the indicated one
	 * @param label new label for the region
	 * @param region region to update, optional. Default to active region
	 */
	export function setRegionLabel(label: Label, region?: Region, ): void {
		// if no region was specified, use the active one by default
		if(!region){
			if(!activeRegion) return;
			region = activeRegion;
		}

		// update region color
		const {color, ...regionsOpt} = region
		region.setOptions({color: label.color, ...regionsOpt});

		// update annotation label
		regionsMap.get(region.id).speaker = label.name;
		updateAnnotations();

		if(region === activeRegion) setActiveRegionBackground(activeRegion.color);
	}

    /**
	 * Update active region background style with the specified color.
	 * @param color new color for the active region
	 */
	export function setActiveRegionBackground(color: string): void{
		if(!activeRegion) return;

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
	 * update annotations with current regions' state and dispatch them toward backend
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
    function isRegionVisible(region: Region, waveformContainer: HTMLDivElement): boolean {
		// Get the left and right boundaries of the waveform view box:
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
	 * Set active region with specified one. Use `null` to
	 * unset active region.
	 * Do nothing if component is not in interactive mode
	 * @param region the region to activate
	 */
	function setActiveRegion(region: Region): void {
		if(!interactive) return;

		if(activeRegion){
			activeRegion.element.style.background = activeRegion.color;
		}

		activeRegion = region;
		if(!activeRegion) return; // in the case where active regin is unset

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
	 * @param direction: selection direction
	 */
	function selectRegion(direction: "backward" | "forward"): void {
		// go back if shift was pressed, else go ahead:
		const step = direction === "backward" ? -1 : 1;
		var regions = getRegions().sort((r1, r2) => r1.start > r2.start ? 1 : -1);
		// if there is no active region, active the first one
		if(activeRegion === null){
			setActiveRegion(regions[0]);
		}
		else{
			var activeRegionIdx = regions.indexOf(activeRegion);
			setActiveRegion(regions.at((activeRegionIdx + step) % regions.length));
		}
	};

	/**
	 * Add a region on the waveform.
	 * @param start	start bound of the region to add, in seconds
	 * @param end end bound of the region to add, in seconds
	 * @param label label associated to the region to add
	 */
    function addRegion(start: number, end: number, label?: Label): Region {
		label = label || caption.getActiveLabel() || caption.getDefaultLabel();
		let region = wsRegions.addRegion({
			start: start,
			end: end,
			color: label.color,
			drag: interactive,
			resize: interactive,
		});
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

		const speaker = regionsMap.get(region.id).speaker;
		const {start, id, ...rightRegionOpt} = region
		const regionRight = addRegion(
			splitTime,
			rightRegionOpt.end,
			caption.getLabel("name", speaker),
		);

		const {end, ...leftRegionOpt} = region
		region.setOptions({end: splitTime, ...leftRegionOpt});

		// annotations need to be updated to take into account the split
		onRegionUpdate(region);

		setActiveRegion(regionRight);
	}

	/**
	 * Remove specified region as well as the mapped annotation
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
	 * Adjust region start and end time boundaries
	 * @param direction shortcut name. Indicates direction: forward or backward.
	 * @param fastMode indicates whether shift key was pressed. If true, move faster
	 * @param side side of the active region to be updated
	 */
    function adjustRegionBounds(direction: "backward" | "forward", side: "start" | "end", fastMode: boolean): void {
		if(!activeRegion) return;

		//TODO do not hardcore this and adapt it according to relative size of the waveform
		let dx: number = (direction === "backward" ? -1 : 1);
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
        ));

        annotations.forEach(annotation => {
            let label = caption.getLabel("name", annotation.speaker, true);
			caption.setActiveLabel(label.shortcut);
            addRegion(
				annotation.start,
            	annotation.end,
            	label,
			);
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
	 * Handle the region creation event. The new added region becomes the active one.
	 * @param region the created region
	 */
	function onRegionCreated(region: Region): void{
		// map an annotation object to current region
		const label = caption.getActiveLabel() || caption.getDefaultLabel();
		const annotation = {start: region.start, end: region.end, speaker: label.name};
		regionsMap.set(region.id, annotation);
		updateAnnotations();

		region.color = label.color;
		region.setOptions(region);

		// if this is the first region added on the waveform
		if(!initialAnnotations){
			initialAnnotations = [annotation];
		}

		// set region as active one
		setActiveRegion(region);
	}

    /**
	 * Handle the region removal event, and remove the active region. According to `key` and
	 * `shiftKey` value, the new active region is the one positioned before or after the removed region.
	 * Do nothing if there is no active region.
	 * @param key shortcut name. Help to determine which region to select after the removal.
	 * @param shiftKey indicates whether shift key was pressed. Help to determine which region to select
	 */
	function onRegionRemove(key: string, shiftKey: boolean): void {
		// if there is no active region, do nothing
		if(!activeRegion) return;

		const region2remove = wsRegions.getRegions().find((region) => region.id === activeRegion.id);
		// remove active region and set the next region as the active one
		if(key === "Delete" || (key == "Backspace" && shiftKey)){
			selectRegion("forward");
		}

		else {
			// remove region and set the previous region as the active one
			selectRegion("backward");
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
	function onTimeAdjustement(key: string, shiftKey: boolean, altKey: boolean): void {
		// if there is an active region, update region bounds
		if(activeRegion){
			const side = (altKey ? "end" : "start");
			const direction = (key === "ArrowLeft"? "backward": "forward")
			adjustRegionBounds(direction, side, shiftKey);
			return;
		}
		// else update time cursor position
		adjustTimeCursorPosition(key, shiftKey);
	}


	$: if(value?.annotations !== null && wsRegions){
		createRegions(value.annotations);
	}

	$: waveform.on("init", () => {
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
			case 1: addRegion(waveform.getCurrentTime() -1, waveform.getCurrentTime() + 1); break;
			case 2: onRegionRemove("Delete", false); break;
			case 3: onRegionSplit(waveform.getCurrentTime()); break;
			case 4: selectRegion("backward"); break;
			case 5: selectRegion("forward");break;
			default: // do nothing
		}
	}

	function onGamepadAxePushed(event: AxeEvent): void {
		let direction = event.value < 0? "ArrowLeft" : "ArrowRight";
		switch(event.idx){
			case 0: onTimeAdjustement(direction, false, false); break;
			case 2: onTimeAdjustement(direction, false, true); break;
			default: // do nothing
		}
	}

	function setMode(newMode: string): void {
		if(!mode && !newMode) return;

		if(mode){
			// disabling mode case
			if(!newMode || mode == newMode){
				document.getElementById(`${mode}-button`).blur();
				mode = "";
				return;
			}
			// switching mode case
			mode = newMode;
		} else{
			// enabling mode case
			 mode = newMode;
			 document.getElementById(`${mode}-button`).focus();
		}
	}

	$: waveform.on("ready", () => {
		if(!wsGamepad){
			wsGamepad = waveform.registerPlugin(GamepadPlugin.create());
			wsGamepad?.on("button-pressed", (e: ButtonEvent) => {
				onGamepadButtonPressed(e);
			});
			wsGamepad?.on("axe-pushed", (e: AxeEvent)=> {
				onGamepadAxePushed(e);
			});
		}

		if(wsRegions){
			// add region-clicked event listener
			wsRegions.on("region-clicked", (region, e) => {
				if(!interactive) return;
				switch(mode){
					case "remove": removeRegion(region); break;
					case "split": splitRegion(region, region.start + (region.end - region.start) / 2); break;
					default: setActiveRegion(region); region.play();
				}
			});

			wsRegions.on("region-created", (region: Region) => {
				onRegionCreated(region);
			});
			wsRegions.on("region-updated", (region) => {
				onRegionUpdate(region);
			});
			wsRegions.on("region-in", (region: Region) => {
				dispatch("region-in", region);
			});
			wsRegions.on("region-out", (region: Region) => {
				dispatch("region-out", region);
			});
		}
	});

	$: waveform.on("dblclick", () => {
			window.alert("To add a new annotation, please drag on an empty space of the waveform.");
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
				case "ArrowLeft": onTimeAdjustement("ArrowLeft", e.shiftKey, e.altKey); break;
				case "ArrowRight": onTimeAdjustement("ArrowRight", e.shiftKey, e.altKey); break;
				case "Escape": setActiveRegion(null); setMode(""); break;
				case "Tab": e.preventDefault(); selectRegion(e.shiftKey? "backward" : "forward"); break;
				case "Delete": onRegionRemove("Delete", e.shiftKey); break;
				case "Backspace": onRegionRemove("Backspace", e.shiftKey); break;
				case "Enter":
					e.preventDefault();
					if(e.shiftKey){
						onRegionSplit(waveform.getCurrentTime());
					} else {
						const currentTime = waveform.getCurrentTime();
						addRegion(currentTime -1, currentTime + 1);
					}
					break;
				default: //do nothing
			}
		});
		// this is needed to keep focus on mode button
		window.addEventListener("click", (e: MouseEvent) => {
			if(!mode) return;
			document.getElementById(`${mode}-button`).focus();
		})
	});

</script>

{#if value && waveform}
	<div class="regions-actions">
		{#if interactive}
			<button
				class="icon"
				aria-label="Reset annotations"
				title={i18n("Reset annotations")}
				on:click={resetRegions}
			>
				<Undo/>
			</button>
		{/if}
		<button
			class="icon"
			id="remove-button"
			aria-label="Remove an annotation"
			title={i18n("Remove an annotation")}
			on:click={() => setMode("remove")}
		>
			<Gum/>
		</button>
		<button
			class="icon"
			id="split-button"
			aria-label="Split an annotation"
			title={i18n("Split an annotation")}
			on:click={() => setMode("split")}
		>
			<Trim/>
		</button>
	</div>
{/if}

<style>
	.regions-actions {
		display: flex;
		justify-self: self-end;
		align-items: center;
	}

	.icon {
		width: var(--size-5);
		width: var(--size-5);
		color: var(--neutral-400);
		margin-left: var(--spacing-md);
		fill: var(--neutral-400);
	}

	.icon:hover, .icon:focus {
		color: var(--color-accent);
	}

</style>
