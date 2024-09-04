<script lang="ts">
    import {onMount} from "svelte";

    export let isOpen: boolean = false;

    let dialog: HTMLDialogElement;

    /**
     * Open the help dialog box
     */
    export function openDialog(): void {
        // open dialog pop-up
        dialog.showModal();
        document.getElementById("help-dialog-box").hidden = false;
        isOpen = true;
    }

    /**
     * Method called when closing event is triggered
     */
    function onClose(): void {
        dialog.close();
        document.getElementById("help-dialog-box").hidden = true;
        isOpen = false;
    }

    onMount(() => {
        window.addEventListener("keydown", (e): void => {
            if(isOpen){
                switch(e.key){
                    case "Escape": onClose(); break;
                }
            }
        });
    });

</script>

<dialog bind:this={dialog} id="help-dialog-box" hidden>
    <p>
        Do you have a problem or a suggestion about this component?
        Feel free to open an issue on the <a href="https://github.com/clement-pages/gryannote/issues/new" target="_blank">gryannote github directory</a>!
    </p>
    <p>
        Component's keyboard shortcuts:
    </p>
    <img src="https://github.com/clement-pages/gryannote/blob/main/docs/assets/shortcuts.png?raw=true" alt="component keyboard shortcut"/>
    <p>
        You can also use a gamepad to speed up your annotation process! Go <a href="https://github.com/clement-pages/gryannote/tree/main/gryannote/audio#gamepad-shortcuts">here</a> for further details.
    </p>
    <button
        id="close"
        on:click={() => onClose()}
    >
        Close
    </button>
</dialog>

<style>
    a {
        font-family: Arial, Helvetica, sans-serif;
        text-decoration-line: underline;
    }

    a:hover {
        color: var(--color-accent);
    }

    p {
        color: var(--body-text-color);
        font-family: Arial, Helvetica, sans-serif;
        margin: 1em;
    }

    #help-dialog-box[hidden] {
        display: none !important;
    }

    #help-dialog-box {
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

    button {
        border: var(--button-border-width) solid;
        border-radius: var(--button-large-radius);
        font-weight: var(--button-large-text-weight);
        padding: var(--button-large-padding);
        margin: 1em;
    }

    #close {
        border-color: var(--button-secondary-border-color);
        color: var(--button-secondary-text-color);
        background: var(--button-secondary-background-fill);
    }

    #close:hover {
        border-color: var(--button-secondary-border-color-hover);
        color: var(--button-secondary-text-color-hover);
        background: var(--button-secondary-background-fill-hover);
    }


    #help-dialog-box::backdrop {
        background: rgba(0, 0, 0, 0.3);
    }

</style>
