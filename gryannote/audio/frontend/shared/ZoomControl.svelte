<script lang="ts">
    import { onMount} from "svelte"
    import WaveSurfer from "@gryannote/wavesurfer.js";
	import GamepadPlugin, {
		type ButtonEvent
	} from "@gryannote/wavesurfer.js/dist/plugins/gamepad";

	export let waveform: WaveSurfer;
	export let wsGamepad: GamepadPlugin;
    export let showZoomSlider: boolean = false;
    export let isDialogOpen: boolean = false;

	let zoomMin: number;
	let zoomMax: number;
    let currentZoom: number;
    let slider: HTMLInputElement;

	enum zoomCoef {
		normalZoom = 1.1,
		fastZoom = 2.0,
	}

	/**
	 * Adjust slider style according to current zoom value
	 */
    function adjustSlider(): void {
        if(!slider) return;

		const cursorPosition = 100 * ((currentZoom - zoomMin) / (zoomMax - zoomMin));
        slider.style.background = `linear-gradient(to right, var(--color-accent) ${
            cursorPosition
        }%, var(--neutral-400) ${cursorPosition}%)`;
    };

    /**
	 * Update zoom value
	 * @param value new value for zoom
	 */
	function zoom(value: number): void{
		if(value < zoomMin){
			currentZoom = zoomMin;
		} else if(value > zoomMax){
			currentZoom = zoomMax;
		} else{
			currentZoom = value;
		}
		waveform.zoom(currentZoom);
		adjustSlider();
	}

	function onGamepadButtonPressed(event: ButtonEvent): void {
		switch(event.idx){
			case 12: zoom(currentZoom * zoomCoef.fastZoom); break;
			case 13: zoom(currentZoom / zoomCoef.fastZoom); break;
			default: // do nothing
		}
	}

	$: waveform?.on("ready", () => {
		// adapt zoom range according to audio duration and waveform viewport size
		const viewSize = waveform.getWrapper().clientWidth;
		const duration = waveform.getDuration();

		// min value of zoom to have all the audio in the waveform viewport
		zoomMin = Math.trunc(viewSize / duration);
		if(zoomMin === 0) zoomMin = 1;
		// the longer the audio, the more we want to be able to zoom in relative to min zoom
		zoomMax = Math.trunc(zoomMin * (duration  / 10));
		currentZoom = zoomMin;

		waveform.zoom(currentZoom);
		adjustSlider();
	});

	$: wsGamepad?.on("button-pressed", (event: ButtonEvent) => onGamepadButtonPressed(event));

    onMount(() => {
        window.addEventListener("keydown", (e) => {
            // do not process keyboard shortcuts when a dialog popup is open
            if(isDialogOpen) return;

			const coef = e.shiftKey ? zoomCoef.fastZoom : zoomCoef.normalZoom;
            switch(e.key){
                case "ArrowUp": e.preventDefault(); zoom(currentZoom * coef); break;
				case "ArrowDown": e.preventDefault(); zoom(currentZoom / coef); break;
                default: //do nothing
            }
        })
    });

</script>

{#if showZoomSlider}
	<input
		bind:this={slider}
		class="zoom-slider"
		type="range"
		min={zoomMin}
		max={zoomMax}
		bind:value={currentZoom}
		on:input={(e) => zoom(e.target.value)}
		on:focusout={() => showZoomSlider = false}
	>
{/if}

<style>
	.zoom-slider {
		-webkit-appearance: none;
		appearance: none;
		width: var(--size-20);
		accent-color: var(--color-accent);
		height: 4px;
		cursor: pointer;
		outline: none;
		border-radius: 15px;
		background-color: var(--neutral-400);
	}

	input[type="range"]::-webkit-slider-thumb {
		-webkit-appearance: none;
		appearance: none;
		height: 15px;
		width: 15px;
		background-color: var(--color-accent);
		border-radius: 50%;
		border: none;
		transition: 0.2s ease-in-out;
	}

	input[type="range"]::-moz-range-thumb {
		height: 15px;
		width: 15px;
		background-color: var(--color-accent);
		border-radius: 50%;
		border: none;
		transition: 0.2s ease-in-out;
	}
</style>
