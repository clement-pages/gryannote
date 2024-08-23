<script lang="ts">
    import { onMount} from "svelte"
    import WaveSurfer from "wavesurfer.js";

	export let zoomMin: number = 1;
	export let zoomMax: number = 500;
    export let currentZoom: number = zoomMin;
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
		console.log(currentZoom);
		waveform.zoom(currentZoom);
	}

    $: currentZoom, adjustSlider();

	// init zoom
	$: waveform?.on("ready", () => {
		waveform.zoom(currentZoom);
		adjustSlider();
	})

    onMount(() => {
        window.addEventListener("keydown", (e) => {
            // do not process keyboard shortcuts when a dialog popup is open
            if(isDialogOpen) return;

			const coef = e.shiftKey ? 2.0 : 1.1;
			console.log(e.key)
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
		bind:this={zoomElement}
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
