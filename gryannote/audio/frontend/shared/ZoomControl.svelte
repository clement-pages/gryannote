<script lang="ts">
    import { onMount} from "svelte"
    import WaveSurfer from "wavesurfer.js";

    export let currentZoom: number = 50;
	export let zoomMin: number = 0;
	export let zoomMax: number = 500;
	export let zoomDelta: number = 50;
    export let showZoomSlider: boolean = false;
    export let waveform: WaveSurfer;
    export let isDialogOpen: boolean = false;

    let zoomElement: HTMLInputElement;

	/**
	 * Adjust slider style according to current zoom value
	 */
    function adjustSlider(): void {
        let slider = zoomElement;
        if(!slider) return;

        slider.style.background = `linear-gradient(to right, var(--color-accent) ${
            currentZoom / 5
        }%, var(--neutral-400) ${currentZoom / 5}%)`;
    };

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

    $: currentZoom, adjustSlider();

    onMount(() => {
        window.addEventListener("keydown", (e) => {
            // do not process keyboard shortcuts when a dialog popup is open
            if(isDialogOpen) return;

            switch(e.key){
                case "ArrowUp": e.preventDefault(); updateZoom(currentZoom + zoomDelta); break;
				case "ArrowDown": e.preventDefault(); updateZoom(currentZoom - zoomDelta); break;
                default: //do nothing
            }
        })
		// init zoom
        waveform.zoom(currentZoom);
		adjustSlider();
    });

</script>

<input
    bind:this={zoomElement}
    class="zoom-slider"
    type="range"
    min={zoomMin}
    max={zoomMax}
    bind:value={currentZoom}
    on:input={(e) => updateZoom(e.target.value)}
    on:focusout={() => showZoomSlider = false}
>

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
