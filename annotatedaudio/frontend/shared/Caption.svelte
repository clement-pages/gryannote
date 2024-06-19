<script lang="ts">
    import type { Label } from "./types";
    import Plus from "./icons/Plus.svelte";
    import { createEventDispatcher, onMount} from "svelte";

    export let defaultLabel: Label | null = null;
    export let activeLabel: Label | null = null;

    let container: HTMLDivElement;

    let labels: Label[] = [];

    let labelIdx: number = 0;

    const colorList = ["rgba(255, 215, 0, 0.5)", "rgba(0, 0, 255, 0.5)", "rgba(255, 0, 0, 0.5)", "rgba(0, 255, 0, 0.5)"];
    const dispatch = createEventDispatcher<{
        select: Label;
    }>();

    /**
     * Create label user interface component
     * @param label
     */
    function createLabelElement(label: Label): void {
        const labelButton = document.createElement("button");
        labelButton.style.backgroundColor = label.color;
        labelButton.id = label.shortcut;
        labelButton.innerHTML = "<span style=\"font-weight: bold;\">" +  label.shortcut + "</span>: " + label.name;
        labelButton.addEventListener("focusin", () => {setActiveLabel(label.shortcut)});
        labelButton.addEventListener("focusout", () => {setActiveLabel()});

        container.appendChild(labelButton);
    }

    /**
     *  Create and add a new label to the caption with specified name, color and shortcut. The new
     * label is return by this method. In the case a label for the specified name already exists,
     * this method does not create a new label and returns the existing one.
     * @param name label name, optional. If not provided, label will be set to LABEL_xx.
     * @param color label color, optional.
     * @param shortcut label shortcut, optional. If not provided, will be set to the first available
     * letter in alphabetic order.
     */
    export function createLabel(options: {name?: string, color?: string, shortcut?: string}): Label {
        // if maximum number of labels has been reached, do nothing
        if(labels.length === 26){
            return;
        }
        if(!options.name){
            options.name = "LABEL_" + labelIdx.toString().padStart(2, "0");
        }
        // if a label with specified name already exists, do not create a new one
         if(getLabel("name", options.name)){
            return getLabel("name", options.name);
        }
    
        if(!options.color){
            options.color = colorList[labelIdx % colorList.length];
        }
        if(!options.shortcut){
            options.shortcut = "A";
            // take the first available letter
            while((labels.some(label => label.shortcut === options.shortcut)) && options.shortcut !== "Z"){
                options.shortcut = String.fromCharCode(options.shortcut.charCodeAt(0) + 1);
            }
        }

        const label: Label = {
            name: options.name,
            color: options.color,
            shortcut: options.shortcut,
        };
        labels.push(label);
        createLabelElement(label);

        labelIdx++;

        labels = labels.sort((i1, i2) => i1.shortcut.localeCompare(i2.shortcut));

        return label;
    }

    /**
     * Get label mapped to specified attribute value. If there is no correspondance, a new label is 
     * created
     * if `create` was set to `true`, otherwise returns `undefined`
     * @param attribute attribute to search
     * @param value attribute value
     * @param create whether to create a label if no correspondance found for specified attribute
     * value
     * 
     * @returns a caption label or `undefined`
     */
    export function getLabel(attribute: string, value: string, create?: boolean): Label {
        if(create === undefined){
            create = false;
        }

        let label = labels.find(label => label[attribute] === value);
        if(label == undefined && create){
            const options = {};
            options[attribute] = value;
            label = createLabel(options);
        }

        return label
    }

    /**
     * Set the label mapped to specified shorcut as the active one
     * @param shortcut shortcut mapped to the label to activate. If shortcut does not correspond
     * to any existing label, a new one will be created and assigned to this shortcut. If not value
     * is specified, will deselect active label, if any.
     */
    function setActiveLabel(shortcut?: string): void {
        let label = null;

        // retrieve label and create it if not found
        if(shortcut !== undefined){
            label = getLabel("shortcut", shortcut.toUpperCase(), true);
        }

        // reset active label
        if(activeLabel){
            document.getElementById(activeLabel.shortcut).classList.remove("active-button");
        }

        // update active label
        activeLabel = label;
        if(activeLabel){
            document.getElementById(activeLabel.shortcut).classList.add("active-button");
            dispatch("select", activeLabel);
        }
    }

    $: if(labels.length > 0){
        defaultLabel = labels[0];
    }

    onMount(() => {
        window.addEventListener("keydown", (e): void => {
            if(e.key.match(/^[a-zA-Z]$/)){
                setActiveLabel(e.key);
            }
            else if(e.key === "Escape"){
                setActiveLabel();
            }
        });
    });
</script>

<div class="caption-container">
    <div class="caption" bind:this={container}></div>
    <div class="action-buttons">
        <button class="create-label" on:click={() => {
                const label = createLabel({});
                setActiveLabel(label.shortcut);
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
