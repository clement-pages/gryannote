<script lang="ts">
    import type { Annotation } from "./types";

    export let value: Annotation[] | null = null;

    let items = [];
    $:{
        // retrieve speaker list and corresponding annotation color
        value.forEach(annotation => {
            if(!items.some(item => item.speaker === annotation.speaker)){
                items = [...items, {speaker: annotation.speaker, color: annotation.color}]
            }
        });
        items = items.sort((i1, i2) => i1.speaker.localeCompare(i2.speaker))
    }
</script>

<div class="caption-component">
    {#each items as item }
        <div class="caption-item-component">
            <button 
                disabled 
                style="background-color: {item.color}"
                class="caption-item"
            >
                {item.speaker}
            </button>
        </div>
    {/each}
</div>

<style>

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

</style>
