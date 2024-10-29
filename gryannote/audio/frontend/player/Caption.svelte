<script lang="ts">
    import type { Label } from "../shared/types";
    import Plus from "../shared/icons/Plus.svelte";
    import Dialog from "../shared/Dialog.svelte";
    import { createEventDispatcher, onMount} from "svelte";
    import GamepadPlugin, {type ButtonEvent} from "@gryannote/wavesurfer.js/dist/plugins/gamepad";

    export let isDialogOpen: boolean = false;
    export let interactive: boolean = true;
    export let wsGamepad: GamepadPlugin;

    let container: HTMLDivElement;
    let labels: Label[] = [];
    let dialog: Dialog;

    let activeLabel: Label | null = null;

    const colorList = ["#ffd70080", "#0000ff80", "#ff000080", "#00ff0080"];
    const dispatch = createEventDispatcher<{
        select: Label;
        name_update: Label,
        color_update: Label;
    }>();

    /**
     * Return active label
     */
     export function getActiveLabel(): Label | null {
        return activeLabel;
    }

    /**
     * Return default label
     */
    export function getDefaultLabel(): Label {
        return labels[0] || createLabel({});
    }

    /**
     * Create label user interface component
     * @param label
     */
    function createLabelElement(label: Label): void {
        const labelButton = document.createElement("button");
        labelButton.id = label.shortcut;

        labelButton.addEventListener("focusin", () => setActiveLabel(label.shortcut));
        labelButton.addEventListener("focusout", () => setActiveLabel());
        labelButton.addEventListener("dblclick", () => dialog.openDialog(label));

        container.appendChild(labelButton);

        updateLabelUI(label);
    }

    /**
     * Create and add a new label to the caption with specified name, color and shortcut. The new
     * label is return by this method. In the case a label for the specified name already exists,
     * this method does not create a new label and returns the existing one.
     * @param name label name, optional. If not provided, label will be set to LABEL_xx.
     * @param color label color, optional.
     * @param shortcut label shortcut, optional. If not provided, will be set to the first available
     * letter in alphabetic order.
     */
    function createLabel(options: {name?: string, color?: string, shortcut?: string}): Label {
        const labelIdx = labels.length;
        // if maximum number of labels has been reached, do nothing
        if(labelIdx === 26){
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

        labels = labels.sort((i1, i2) => i1.shortcut.localeCompare(i2.shortcut));

        return label;
    }

    /**
     * Get label mapped to specified attribute value. If there is no correspondence, a new label is
     * created
     * if `create` was set to `true`, otherwise returns `undefined`
     * @param attribute attribute to search
     * @param value attribute value
     * @param create whether to create a label if no correspondence found for specified attribute
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
     * Update the User Interface of the specified label.
     * @param label label to update
     */
    function updateLabelUI(label: Label): void {
        let labelButton = document.getElementById(label.shortcut);
        labelButton.style.backgroundColor = label.color;
        labelButton.innerHTML = "<span style=\"font-weight: bold;\">" + label.shortcut + "</span>: " + label.name;
    }

    /**
     * Update label with specified options inplace
     * @param label
     * @param options new values for name, color and shortcut
     */
    function updateLabel(label: Label, options: Partial<Label> = {}): void {
        const {name = label.name, color = label.color, shortcut = label.shortcut} = options;

        if(label.name !== name){
            label.name = name;
            // update annotation name
            dispatch("name_update", label);
        }

        if(label.color !== color){
            label.color = color;
            // update regions color
            dispatch("color_update", label);
        }
        // Do not update label's shortcut if another label already use the new value for this prop
        if(!labels.find(_label => _label.shortcut === shortcut)){
            let labelButton = document.getElementById(label.shortcut);
            label.shortcut = shortcut;
            // update label element id
            labelButton.id = label.shortcut;
        }
        updateLabelUI(label);
    }

    /**
     * Set the label mapped to specified shortcut as the active one
     * @param shortcut shortcut mapped to the label to activate. If shortcut does not correspond
     * to any existing label, a new one will be created and assigned to this shortcut. If not value
     * is specified, will deselect active label, if any.
     */
    function setActiveLabel(shortcut?: string): void {
        let label = null;

        // retrieve label and create it if not found
        if(shortcut !== undefined){
            label = getLabel("shortcut", shortcut, true);
        }

        // reset active label
        if(activeLabel){
            document.getElementById(activeLabel.shortcut).classList.remove("active-button");
            document.getElementById(activeLabel.shortcut).blur();
        }

        // update active label
        activeLabel = label;
        if(activeLabel){
            document.getElementById(activeLabel.shortcut).classList.add("active-button");
            document.getElementById(activeLabel.shortcut).focus();
            dispatch("select", activeLabel);
        }
    }

    function onGamepadAxeValueUpdated(event: ButtonEvent): void {
        let activeLabelIdx = labels.findIndex((label) => label.shortcut === activeLabel?.shortcut);
        switch(event.idx){
            case 14: setActiveLabel(labels.at(activeLabelIdx - 1 % labels.length).shortcut); break;
            case 15: setActiveLabel(labels.at((activeLabelIdx + 1) % labels.length).shortcut); break;
            default: // do nothing
        }
    }

    $: wsGamepad?.on("button-pressed", (e: ButtonEvent) => onGamepadAxeValueUpdated(e));

    onMount(() => {
        window.addEventListener("keydown", (e): void => {
            // do not process keyboard shortcuts when a dialog popup is open
            if(isDialogOpen) return;

            // if component is in static mode, do not allow to use keyboard shortcuts
            if(!interactive) return;

            if(e.key.match(/^[a-zA-Z]$/)){
                let shortcut = e.key.toUpperCase();
                setActiveLabel(shortcut);
            }
            else if(e.key === "Escape"){
                setActiveLabel();
            }
            else if(e.key === "F2" && activeLabel){
                dialog.openDialog(activeLabel);
            }
        });
    });
</script>

<div class="caption-container">
    <div class="caption" bind:this={container}></div>
    <div class="action-buttons">
        {#if interactive}
            <button class="create-label" on:click={() => {
                    const label = createLabel({});
                    setActiveLabel(label.shortcut);
                }}>
                <Plus/>
            </button>
        {/if}
    </div>
</div>

<Dialog
    bind:this={dialog}
    bind:isOpen={isDialogOpen}
    on:submit={(e) => {
        let label = labels.find(_label => _label.shortcut === e.detail.shortcut);
        updateLabel(label, e.detail);
    }}
/>

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
