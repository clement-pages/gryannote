<script lang="ts">
    import {createEventDispatcher, onMount} from "svelte";

    export let title: string = "";
    export let isOpen: boolean = false;

    let name: string;
    let color: string;
    let shortcut: string;

    let dialog: HTMLDialogElement;

    const dispatch = createEventDispatcher<{
        submit: {name?:string, color?: string, shortcut?:string};
    }>();

    export function openDialog(labelID: string): void {
        dialog.showModal();
        shortcut = labelID;
        isOpen = true;
    }

    function onClose(): void {
        dialog.close();
        name = color = shortcut = undefined;
        isOpen = false;
    }

    function onSubmit(): void {
        dispatch("submit", {name, color, shortcut});
        onClose();
    }

    onMount(() => {
        window.addEventListener("keydown", (e): void => {
            if(isOpen){
                switch(e.key){
                    case "Enter": onSubmit(); break;
                }
            }
        });
    });

</script>

<dialog bind:this={dialog}>
    <h2> {title} </h2>
    <input type="text" bind:value={name}>
    <button on:click={onSubmit}>Submit</button>
    <button on:click={onClose}>Close</button>
</dialog>
