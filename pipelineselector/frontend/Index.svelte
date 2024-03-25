<script context="module" lang="ts">
	export { default as BaseDropdown } from "./shared/Dropdown.svelte";
	export { default as BaseMultiselect } from "./shared/Multiselect.svelte";
	export { default as BaseExample } from "./Example.svelte";
</script>

<script lang="ts">
	import Dropdown from "./shared/Dropdown.svelte";
	import { Block } from "@gradio/atoms";
	import { StatusTracker } from "@gradio/statustracker";

	import type { Gradio, KeyUpData } from "@gradio/utils";
	import type { LoadingStatus } from "@gradio/statustracker";
	import PipelineInfo from "./shared/PipelineInfo" 

	export let label = "Dropdown";
	export let info: string | undefined = undefined;
	export let elem_id = "";
	export let elem_classes: string[] = [];
	export let visible = true;
	export let value: PipelineInfo | null = null;
	export let value_is_output = false;
	export let choices: [string, string | number][];
	export let show_label: boolean;
	export let filterable: boolean;
	export let container = true;
	export let scale: number | null = null;
	export let min_width: number | undefined = undefined;
	export let loading_status: LoadingStatus;
	export let allow_custom_value = false;
	export let enable_token_entry = true;
	export let gradio: Gradio<{
		change: typeof value;
		input: never;
		select: typeof value;
		blur: never;
		focus: never;
		key_up: KeyUpData;
	}>;
	export let interactive: boolean;

	let token: string = "";

	/**
	 * Handle drop down selection event
	 * @param name name of the selected pipeline
	 */
	function handleSelect(name: string): void {
		if(name !== ""){
			if(value === null){
				value = new PipelineInfo({name, token});
			} else {
				value.name = name;
			}
			gradio.dispatch("select", value);
		}
	}
</script>

<Block
	{visible}
	{elem_id}
	{elem_classes}
	padding={container}
	allow_overflow={false}
	{scale}
	{min_width}
>
	<StatusTracker
		autoscroll={gradio.autoscroll}
		i18n={gradio.i18n}
		{...loading_status}
	/>

	{#if visible}
		{#if enable_token_entry}
			<label class:container>
				<input
					data-testid="textbox"
					type="text"
					class="text-area"
					bind:value={token}
					placeholder="hf_xxxxxxx..."
					disabled={!interactive}
				/>
			</label>
		{/if}
		<Dropdown
			bind:value_is_output
			{choices}
			{label}
			{info}
			{show_label}
			{filterable}
			{allow_custom_value}
			{container}
			on:change={() => gradio.dispatch("change")}
			on:input={() => gradio.dispatch("input")}
			on:select={(e) => handleSelect(e.detail.value)}
			on:blur={() => gradio.dispatch("blur")}
			on:focus={() => gradio.dispatch("focus")}
			on:key_up={(e) => gradio.dispatch("key_up", e.detail)}
			disabled={!interactive}
		/>
	{/if}
</Block>


<style>

	.text-area {
		color: black;
	}

</style>