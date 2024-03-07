<script lang="ts">
    import type { Annotation, CaptionItem } from "./types";
    import { createEventDispatcher, onMount} from "svelte";

    export let value: Annotation[] | null = null;

    let captionItems: CaptionItem[] = [];
    let activeItem = null;

    const dispatch = createEventDispatcher<{
        select: CaptionItem;
    }>();

    function handleCaptionButtonSelection(key: string): void {
        if(key === "Escape" && activeItem){
            // reset active item
            document.getElementById(activeItem.shortcut).classList.remove("active-button");
            activeItem = null;
            return;
        }

        let item = captionItems.find((_item) => _item.shortcut === key.toUpperCase());
        if(item === undefined){
            return;
        }

        // reset active item
        if(activeItem){
            document.getElementById(activeItem.shortcut).classList.remove("active-button");
        }
        activeItem = item;
        document.getElementById(activeItem.shortcut).classList.add("active-button");
        dispatch("select", activeItem);
    }

    $:{
        // retrieve speaker list and corresponding annotation color
        let shortcut = "A";
        value.forEach(annotation => {
            if(!captionItems.some(item => item.speaker === annotation.speaker)){
                let item = {
                    speaker: annotation.speaker,
                    color: annotation.color,
                    shortcut: shortcut,
                }
                captionItems = [...captionItems, item];
                // register keyboard shortcut for current speaker item

                shortcut = String.fromCharCode(shortcut.charCodeAt(0) + 1);
            }
        });
        captionItems = captionItems.sort((i1, i2) => i1.shortcut.localeCompare(i2.shortcut));
    }

    onMount(() => {
        window.addEventListener("keydown", (e): void => {
            handleCaptionButtonSelection(e.key);
        });
    });
</script>

<div class="caption-component">
    {#each captionItems as item }
        <div class="caption-item-component">
            <button 
                style="background-color: {item.color}"
                class="caption-item"
                id={item.shortcut}
                on:focusin={() => handleCaptionButtonSelection(item.shortcut)}
                on:focusout={() => handleCaptionButtonSelection("Escape")}
            >
                <span class="shortcut-letter">{item.shortcut}</span>{": " + item.speaker}
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

.caption-item-component {
    display: inline-block;
    margin: 0.5em;
}

.caption-item{
    padding-left: 0.5em;
    padding-right: 0.5em;
}

.shortcut-letter  {
    font-weight: bold;
}

</style>
