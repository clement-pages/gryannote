<script lang="ts">
    import {createEventDispatcher, onMount} from "svelte";
    import type {Label} from "./types"

    export let isOpen: boolean = false;

    let name: string;
    let color: string;
    let shortcut: string;

    let dialog: HTMLDialogElement;

    const dispatch = createEventDispatcher<{
        submit: {name?:string, color?: string, shortcut?:string};
    }>();

    export function openDialog(label: Label): void {
        name = label.name;
        color = label.color.slice(0, label.color.length - 2);

        // open dialog box
        dialog.showModal();
        document.getElementById("dialog-box").hidden = false;
        document.getElementById("name").focus();
        isOpen = true;
    }

    function onClose(): void {
        dialog.close();
        name = color = shortcut = undefined;
        document.getElementById("dialog-box").hidden = true;
        isOpen = false;
    }

    function onSubmit(): void {
        // color + "80" => set opacity color to 0.5
        dispatch("submit", {name, color: color + "80", shortcut});
        onClose();
    }

    onMount(() => {
        window.addEventListener("keydown", (e): void => {
            if(isOpen){
                switch(e.key){
                    case "Enter": onSubmit(); break;
                    case "Escape": onClose(); break;
                }
            }
        });
    });

</script>

<dialog bind:this={dialog} class="dialog-box" id="dialog-box" hidden>
    <label for="name">Label name:</label>
    <input type="text" maxlength="30" bind:value={name} id="name" name="name">
    <label for="color">Label color:</label>
    <input type="color" bind:value={color} id="color" name="color">
    <div class="dialog-buttons" id="color">
        <button on:click={onClose} id="cancel" >Cancel</button>
        <button on:click={onSubmit} id="submit">Submit</button>
    </div>
</dialog>

<style>
    .dialog-box[hidden] {
        display: none !important;
    }

    .dialog-box {
        display: flex;
        flex-direction: column;
        align-items: center;

        background: var(--block-background-fill);

        border-color: var(--block-border-color);
        border-radius: var(--block-radius);
        border-width: var(--block-border-width);
        box-shadow: var(--block-shadow);

        font-family: Arial, Helvetica, sans-serif;
    }

    .dialog-box::backdrop {
        background: rgba(0, 0, 0, 0.3);
    }

    label {
        color: var(--button-secondary-text-color);
        font-family: inherit;
    }

    input {
        border: 1px solid;
        border-color: var(--block-border-color);
        border-radius: var(--block-radius);
        color: var(--button-secondary-text-color);
        margin: 0.5em;
    }

    .dialog-buttons {
        display: flex;
        flex-direction: row;
    }

    button {
        border: var(--button-border-width) solid;
        border-radius: var(--button-large-radius);
        font-weight: var(--button-large-text-weight);
        padding: var(--button-large-padding);
        margin: 1em;
    }

    #cancel {
        border-color: var(--button-secondary-border-color);
        color: var(--button-secondary-text-color);
        background: var(--button-secondary-background-fill);
    }

    #cancel:hover {
        border-color: var(--button-secondary-border-color-hover);
        color: var(--button-secondary-text-color-hover);
        background: var(--button-secondary-background-fill-hover);
    }

    #submit {
        border-color: var(--button-primary-border-color);
        color: var(--button-primary-text-color);
        background: var(--button-primary-background-fill);
    }

    #submit:hover {
        border-color: var(--button-primary-border-color-hover);
        color: var(--button-primary-text-color-hover);
        background: var(--button-primary-background-fill-hover);
    }
</style>
