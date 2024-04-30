<script lang="ts">
    import type { Annotation, CaptionLabel } from "./types";
    import Plus from "./icons/Plus.svelte";
    import { createEventDispatcher, onMount} from "svelte";

    export let annotations: Annotation[] | null = null;

    let container: HTMLDivElement;

    let labels: CaptionLabel[] = [];
    let activeLabel = null;

    let speakerIdx: number = 0;

    const colorList = ["rgba(255, 215, 0, 0.5)", "rgba(0, 0, 255, 0.5)", "rgba(255, 0, 0, 0.5)", "rgba(0, 255, 0, 0.5)"];
    const dispatch = createEventDispatcher<{
        select: CaptionLabel;
    }>();

    function createLabelElement(label: CaptionLabel): void {
        const labelButton = document.createElement("button");
        labelButton.style.backgroundColor = label.color;
        labelButton.classList.add("captionLabel");
        labelButton.id = label.shortcut;
        labelButton.innerHTML = "<span style=\"font-weight: bold;\">" +  label.shortcut + "</span>: " + label.speaker;
        labelButton.addEventListener("focusin", () => {handleKeyboardSelection(label.shortcut)});
        labelButton.addEventListener("focusout", () => {handleKeyboardSelection("Escape")});

        container.appendChild(labelButton);
    }


    export function createLabel(speaker?: string, color?: string, shortcut?: string): CaptionLabel {
        // if maximum number of labels has been reached, do nothing
        if(labels.length === 26){
            return;
        }
        if(!speaker){
            speaker = "LABEL_" + speakerIdx.toString().padStart(2, "0");
        }
        if(!color){
            color = colorList[speakerIdx % colorList.length];
        }
        if(!shortcut){
            shortcut = "A";
            //take the first available letter
            while((labels.some(label => label.shortcut === shortcut)) && shortcut !== "Z"){
                shortcut = String.fromCharCode(shortcut.charCodeAt(0) + 1);
            }
        }

        const label: CaptionLabel = {
            speaker: speaker,
            color: color,
            shortcut: shortcut,
        };
        labels.push(label);

        createLabelElement(label);

        speakerIdx++;

        return label;
    }

    function setActiveLabel(label: CaptionLabel): void {
        // reset active label
        if(activeLabel){
            document.getElementById(activeLabel.shortcut).classList.remove("active-button");
        }

        // update active label
        activeLabel = label;
        document.getElementById(activeLabel.shortcut).classList.add("active-button");
        dispatch("select", activeLabel);
    }

    function handleKeyboardSelection(key: string): void {
        let label = null

        if(key !== "Escape"){
            label = labels.find((_label) => _label.shortcut === key.toUpperCase());
            // if current key does not correspond to any label, create a new one
            if(!label){
                label = createLabel(undefined, undefined , key.toUpperCase());
            }
        }
        setActiveLabel(label);
    }

    $:{
        if(container && annotations){
            // retrieve speaker list and corresponding annotation color
            annotations.forEach(annotation => {
                // if annotation has a label that does not already exist in the caption,
                // create a new label
                if(!labels.some(label => label.speaker === annotation.speaker)){
                    createLabel(annotation.speaker, annotation.color);
                }
            });
            labels = labels.sort((i1, i2) => i1.shortcut.localeCompare(i2.shortcut));
        }
    }

    onMount(() => {
        window.addEventListener("keydown", (e): void => {
            if(e.key.match(/^[a-zA-Z]$/) || e.key === "Escape"){
                handleKeyboardSelection(e.key);
            }
        });
    });
</script>

<div class="caption-container">
    <div class="caption" bind:this={container}></div>
    <div class="action-buttons">
        <button class="create-label" on:click={() => {
                const label = createLabel();
                setActiveLabel(label);
            }}>
             <Plus/>
        </button>
    </div>
</div>

<style>

.caption-container {
    display: flex;
    justify-content: center;
    margin-top: 1em;
}

div:global(.caption-container button){
    display: inline-block;
    padding: 0.0em 0.5em;
    margin: 0.2em 0.5em;
}

div:global(.caption-container button):hover{
    border-color: var(--color-accent);
}

:global(button.active-button) {
    border-width: 2px;
    border-color: var(--color-accent);
}

.create-label{
    width: 2.25em;
    height: 2.25em;
    fill: var(--neutral-400);
}

.create-label:hover{
    fill: var(--color-accent);
}

</style>
