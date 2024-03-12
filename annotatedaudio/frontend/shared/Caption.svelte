<script lang="ts">
    import type { Annotation, CaptionLabel } from "./types";
    import { createEventDispatcher, onMount} from "svelte";

    export let value: Annotation[] | null = null;

    let captionLabels: CaptionLabel[] = [];
    let activeLabel = null;

    const dispatch = createEventDispatcher<{
        select: CaptionLabel;
    }>();

    function selectActiveLabel(key: string): void {
        if(key === "Escape" && activeLabel){
            // reset active label
            document.getElementById(activeLabel.shortcut).classList.remove("active-button");
            activeLabel = null;
        }
        else{
            let label = captionLabels.find((_label) => _label.shortcut === key.toUpperCase());
            // if current key does not correspond to any label, do nothing
            if(label === undefined){
                return;
            }

            // update active label
            if(activeLabel){
                document.getElementById(activeLabel.shortcut).classList.remove("active-button");
            }
            activeLabel = label;
            document.getElementById(activeLabel.shortcut).classList.add("active-button");
            }
        dispatch("select", activeLabel);
    }

    $:{
        // retrieve speaker list and corresponding annotation color
        let shortcut = "A";
        value.forEach(annotation => {
            if(!captionLabels.some(label => label.speaker === annotation.speaker)){
                let label = {
                    speaker: annotation.speaker,
                    color: annotation.color,
                    shortcut: shortcut,
                }
                captionLabels = [...captionLabels, label];
                shortcut = String.fromCharCode(shortcut.charCodeAt(0) + 1);
            }
        });
        captionLabels = captionLabels.sort((i1, i2) => i1.shortcut.localeCompare(i2.shortcut));
    }

    onMount(() => {
        window.addEventListener("keydown", (e): void => {
            selectActiveLabel(e.key);
        });
    });
</script>

<div class="caption-component">
    {#each captionLabels as label }
        <div class="caption-label-component">
            <button 
                style="background-color: {label.color}"
                class="caption-label"
                id={label.shortcut}
                on:focusin={() => selectActiveLabel(label.shortcut)}
                on:focusout={() => selectActiveLabel("Escape")}
            >
                <span class="shortcut-letter">{label.shortcut}</span>{": " + label.speaker}
            </button>
        </div>
    {/each}
</div>

<style>

:global(button.active-button) {
    border-width: 2px;
    border-color: var(--color-accent);
}

.caption-component {
    justify-content: center;
    display: flex;
}

.caption-label-component {
    display: inline-block;
    margin: 0.5em;
}

.caption-label{
    padding-left: 0.5em;
    padding-right: 0.5em;
}

.shortcut-letter  {
    font-weight: bold;
}

</style>
