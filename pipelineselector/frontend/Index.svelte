<script context="module" lang="ts">
	export { default as BaseDropdown } from "./shared/Dropdown.svelte";
	export { default as BaseMultiselect } from "./shared/Multiselect.svelte";
	export { default as BaseExample } from "./Example.svelte";
</script>

<script lang="ts">
	import Dropdown from "./shared/Dropdown.svelte";
	import { Block } from "@gradio/atoms";
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
			// dispatch event to backward
			gradio.dispatch("select", value);

			// clear parameters:
			document.getElementById("params-control").replaceChildren();
		}
	}

	function object2Map(obj?: Object) {
		const map = new Map<string, any>();
		if(!obj){
			return map;
		}

		for(const key in obj) {
			if(obj.hasOwnProperty(key)) {
				if(typeof obj[key] == "object" && obj[key] !== null) {
					map.set(key, object2Map(obj[key]));
				} else {
					map.set(key, obj[key]);
				}
			}
		}
		return map;
	}

	function addDropdown(container: HTMLElement, name: string, choices: string[], value: string, id?: string): void {
		const label = document.createElement("label");
		label.textContent = name;
		container.appendChild(label);

		const dropdown = document.createElement("select");
		choices.forEach((choice) => {
			const option = document.createElement("option");
			option.textContent = choice;
			option.value = choice;
			dropdown.appendChild(option);
			if(choice === value){
				option.selected = true;
			}
		});

		container.appendChild(dropdown);
	}

	function addSlider(
		container: HTMLElement,
		name: string,
		min: string,
		max: string,
		value: string,
		step: string,
		id?: string
	): void {
		let textboxID = name + "-textbox"
		// add slider label
		const label = document.createElement("label");
		label.textContent = name;
		container.appendChild(label);

		// add slider
		const slider = document.createElement("input");
		slider.type = "range";
		slider.min = min;
		slider.max = max;
		slider.value = value;
		slider.step = step;
		slider.addEventListener("input", (event) => {
			const textbox = document.getElementById(name + "-textbox");
			textbox.value = slider.value;
		});
		container.appendChild(slider);

		// add corresponding text box
		addTextbox(container, name, value, true, false, name + "-textbox");
	}

	function addTextbox(container: HTMLElement, name: string, value: string, editable: boolean, show_label: boolean, id?: string): void {
		if(show_label){
			const label = document.createElement("label");
			label.textContent = name;
			container.appendChild(label);
		}

		const boxvalue = document.createElement("input");
		boxvalue.type = "text";
		boxvalue.value = value;
		boxvalue.contentEditable = String(editable);
		boxvalue.classList.add("text-area");
		if(id){
			boxvalue.id = id;
		}
		container.appendChild(boxvalue);
	}

	function addFormElements(container: HTMLElement, param_specs : Map<string, Map<string, any>>): void {
		param_specs.forEach((specs, name) => {
			if (specs.size == 1){
				// handle nested parameters
				addFormElements(container, specs);
			} else {
				const element = document.createElement("div");
				container.appendChild(element);
				switch(specs.get("component")){
					case "slider": addSlider(element, name, specs.get("min"), specs.get("max"), specs.get("value"), specs.get("step")); break;
					case "dropdown": addDropdown(element, name, specs.get("choices"), specs.get("value")); break;
					case "textbox": addTextbox(element, name, specs.get("value"), false, true); break;
				}
			}
		});
	}

	$: {
		if(value?.param_specs){
			const container = document.getElementById("params-control");
			let param_specs = object2Map(value?.param_specs);
			addFormElements(container, param_specs);
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
			<div class="params-control" id="params-control"></div>
		</div>
	{/if}
</Block>


<style>
	.form {
		display: flex;
		flex-direction: column;
		justify-content: space-around;
	}


	.params-control {
		color: black;
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