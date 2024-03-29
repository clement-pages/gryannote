<script context="module" lang="ts">
	export { default as BaseDropdown } from "./shared/Dropdown.svelte";
	export { default as BaseMultiselect } from "./shared/Multiselect.svelte";
	export { default as BaseExample } from "./Example.svelte";
</script>

<script lang="ts">
	import Dropdown from "./shared/Dropdown.svelte";
	import { Block, BlockTitle } from "@gradio/atoms";
	import { StatusTracker } from "@gradio/statustracker";
	import PipelineInfo from "./shared/PipelineInfo" 

	import type { Gradio, KeyUpData } from "@gradio/utils";
	import type { LoadingStatus } from "@gradio/statustracker";

	export let label: string = "";
	export let info: string | undefined = undefined;
	export let elem_id = "";
	export let elem_classes: string[] = [];
	export let visible = true;
	export let value: PipelineInfo | null = null;
	export let value_is_output = false;
	export let pipelines: [string, string | number][];
	export let show_label: boolean;
	export let container = true;
	export let scale: number | null = null;
	export let min_width: number | undefined = undefined;
	export let loading_status: LoadingStatus;
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

	$: console.log(value);
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
		<div class="form">
			<div class="form-element">
				<label for="token" class="label"> Enter your Hugging Face token:</label>
				<input
					data-testid="textbox"
					type="text"
					class="text-area"
					name="token"
					id="token"
					placeholder="hf_xxxxxxx..."
					aria-label="Enter your Hugging Face token"
					maxlength="50"
					disabled={!interactive}
					bind:value={token}
				/>
			</div>
			<div class="form-element">
				<Dropdown
					bind:value_is_output
					choices={pipelines}
					value={value ? value.name : pipelines[0][0]}
					label={"Select the pipeline to use: "}
					{info}
					{show_label}
					{container}
					on:change={() => gradio.dispatch("change")}
					on:input={() => gradio.dispatch("input")}
					on:select={(e) => handleSelect(e.detail.value)}
					on:blur={() => gradio.dispatch("blur")}
					on:focus={() => gradio.dispatch("focus")}
					on:key_up={(e) => gradio.dispatch("key_up", e.detail)}
					disabled={!interactive}
				/>
			</div>
		</div>
	{/if}
</Block>


<style>

	.form {
		display: flex;
		flex-direction: column;
		justify-content: space-around;
	}

	.label {
		font-size: var(--input-text-size);
		font-weight: var(--input-text-weight);
	}

	.text-area {
		display: block;
		position: relative;
		outline: none !important;
		box-shadow: var(--input-shadow);
		background: var(--input-background-fill);
		padding: var(--input-padding);
		width: 100%;
		color: var(--body-text-color);
		font-weight: var(--input-text-weight);
		font-size: var(--input-text-size);
		line-height: var(--line-sm);
		border: var(--input-border-width) solid var(--border-color-primary);
	}

	.form-element {
		display: flex;
		flex-direction: column;
		justify-content: space-between;
		margin-bottom: 2em;
	}

	input::placeholder {
		color: var(--input-placeholder-color);
	}

</style>