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
	import { BaseButton } from "@gradio/button";

	import { type Gradio, type KeyUpData } from "@gradio/utils";
	import type { LoadingStatus } from "@gradio/statustracker";

	export let info: string | undefined = undefined;
	export let elem_id = "";
	export let elem_classes: string[] = [];
	export let visible = true;
	export let value: PipelineInfo = new PipelineInfo({name:"", token:""});
	export let value_is_output = false;
	export let pipelines: [string, string | number][];
	export let show_label: boolean;
	export let show_config: boolean = false;
	export let enable_edition: boolean = false;
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

	let paramsViewNeedUpdate = false;

	/**
	 * Handle drop down selection event
	 * @param name name of the selected pipeline
	 */
	function handleSelect(name: string): void {
		if(name !== ""){
			value.name = name;
			// reset pipeline's parameters
			value.param_specs = {};
			// dispatch event to backward
			gradio.dispatch("select", value);
			paramsViewNeedUpdate = true;
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

	function Map2Object(map: Map<any, any>): Object {
		let obj = Object.fromEntries(Array.from(
				map.entries(), ([ k, v ]) =>
				v instanceof Map ? [ k, Map2Object(v) ]: [ k, v ]
			)
		);
		return obj;
	}

	function updateParameter(name: string, val: string): void {
		const parents = name.split("-");
		let param_specs = object2Map(value.param_specs);
		var subset = param_specs;
		parents.forEach((parent) => {
			subset = subset.get(parent);
		});
		subset.set("value", val);
		value.param_specs = Map2Object(param_specs);
	}

	function addLabel(container: HTMLElement, value: string): void {
		const label = document.createElement("label");
		label.textContent = value;
		container.appendChild(label);
	}

	function addDropdown(container: HTMLElement, choices: string[], value: string): void {
		const dropdown = document.createElement("select");
		const paramName = container.id;

		addLabel(container, paramName.split("-").at(-1));

		// add dropdown label
		choices.forEach((choice) => {
			const option = document.createElement("option");
			option.textContent = choice;
			option.value = choice;
			dropdown.appendChild(option);
			if(choice === value){
				option.selected = true;
			}
		});
		dropdown.addEventListener("change", (event) => {
			updateParameter(paramName, dropdown.value);
		});
		container.appendChild(dropdown);
	}

	function addSlider(
		container: HTMLElement,
		min: string,
		max: string,
		value: string,
		step: string,
	): void {
		const slider = document.createElement("input");
		const boxvalue = document.createElement("input");
		const paramName = container.id;

		// add slider label
		addLabel(container, paramName.split("-").at(-1));

		// add slider
		slider.type = "range";
		slider.min = min;
		slider.max = max;
		slider.value = value;
		slider.step = step;
		slider.addEventListener("input", (event) => {
			boxvalue.value = slider.value;
			updateParameter(paramName, slider.value);
		});
		container.appendChild(slider);

		// add corresponding text box
		boxvalue.type = "number";
		boxvalue.min = min;
		boxvalue.max = max;
		boxvalue.value = value;
		boxvalue.step = step;
		boxvalue.contentEditable = "true";
		boxvalue.addEventListener("input", (event) => {
			slider.value = boxvalue.value;
			updateParameter(paramName, slider.value);
		});
		container.appendChild(boxvalue);
	}

	function addTextbox(container: HTMLElement, value: string, editable: boolean): void {
		const boxvalue = document.createElement("input");
		const paramName = container.id;

		// add label
		addLabel(container, paramName.split("-").at(-1));

		boxvalue.type = "number";
		boxvalue.value = value;
		boxvalue.contentEditable = String(editable);
		container.appendChild(boxvalue);
	}

	function addFormElements(container: HTMLElement, param_specs : Map<string, Map<string, any>>, parent?: string): void {
		param_specs.forEach((specs, name) => {
			const id = (parent ? parent + "-" : "") + name;
			if (specs.values().next().value instanceof Map){
				// handle nested parameters
				const fieldset = document.createElement("fieldset");
				fieldset.innerHTML = "<legend>" + id + "<legend>";
				fieldset.id = id;
				container.appendChild(fieldset);
				addFormElements(fieldset, specs, name);
			} else {
				const element = document.createElement("div");
				element.id = id
				element.classList.add("param");
				container.appendChild(element);
				switch(specs.get("component")){
					case "slider": addSlider(element, specs.get("min"), specs.get("max"), specs.get("value"), specs.get("step")); break;
					case "dropdown": addDropdown(element, specs.get("choices"), specs.get("value")); break;
					case "textbox": addTextbox(element, specs.get("value"), false); break;
				}
			}
		});
	}

	$: {
		// if a pipeline has been instantiated, and if the parameter view needs to be updated
		if(Object.keys(value.param_specs).length > 0 && paramsViewNeedUpdate){
			const container = document.getElementById("params-control");

			// reset parameter view
			container.replaceChildren();
			if(show_config){
				let param_specs = object2Map(value.param_specs);
				addFormElements(container, param_specs);

				paramsViewNeedUpdate = false;
			}
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
			bind:value={value.token}
		/>
		<Dropdown
			bind:value_is_output
			choices={pipelines}
			label={"Select the pipeline to use: "}
			{info}
			{show_label}
			{container}
			on:input={() => gradio.dispatch("input")}
			on:select={(e) => handleSelect(e.detail.value)}
			on:blur={() => gradio.dispatch("blur")}
			on:focus={() => gradio.dispatch("focus")}
			on:key_up={(e) => gradio.dispatch("key_up", e.detail)}
			disabled={!interactive}
		/>
		{#if enable_edition}
			<div class="toggle-config">
				<p> Show configuration </p>
				<label
					class="switch"
					title={value.name == ""?
						"Please select a pipeline first":
						"Show pipeline config"
					}
				>
					<input
						type="checkbox"
						disabled={value.name == ""}
						bind:checked={show_config}
						on:input={() => {paramsViewNeedUpdate=true; show_config = !show_config }}
					>
					<span class="slider round"></span>
				</label>
			</div>
		{/if}
		<div class="params-control" id="params-control"></div>
			{#if value.name !== ""}
				<div class="validation">
					<BaseButton
						{elem_id}
						{elem_classes}
						{scale}
						{min_width}
						visible={show_config}
						on:click={() => gradio.dispatch("change", value)}
					>
						Update parameters
					</BaseButton>
				</div>
			{/if}
		</div>
	{/if}
</Block>


<style>

	.params-control{
		width: 100%;
	}

	div:global(.params-control fieldset){
		width: inherit;
		border-radius: var(--input-radius);
		border: var(--input-border-width) solid var(--border-color-primary);
		margin: 10px;
	}

	div:global(.params-control legend){
		font-family: inherit;
		font-size: var(--input-text-size);
		font-weight: bold;
	}

	div:global(.params-control .param){
		display: flex;
		justify-content: space-between;
		padding: 5px;
	}

	div:global(.params-control label),
	div:global(.params-control select),
	div:global(.params-control input[type="number"]){
		background-color: inherit;
		font-family: inherit;
		font-size: var(--input-text-size);
	}

	div:global(.params-control select),
	div:global(.params-control input[type="number"]){
		border-radius: var(--input-radius);
		border: var(--input-border-width) solid var(--border-color-primary);
	}

	div:global(.params-control input[type="number"]:invalid){
		border: var(--input-border-width) solid red;
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
		border-radius: var(--input-radius);
	}

	input::placeholder {
		color: var(--input-placeholder-color);
	}


	.toggle-config {
		margin: 1em 1em 1em 0em;
	}

	.switch {
		position: relative;
		display: inline-block;
		width: 60px;
		height: 34px;
	}

	.switch input {
		opacity: 0;
		width: 0;
		height: 0;
	}

	.slider {
		position: absolute;
		cursor: pointer;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background-color: #ccc;
		-webkit-transition: .4s;
		transition: 0.4s;
	}

	.slider:before {
		position: absolute;
		content: "";
		height: 26px;
		width: 26px;
		left: 4px;
		bottom: 4px;
		background-color: var(--input-background-fill);
		-webkit-transition: .4s;
		transition: .4s;
	}

	input:checked + .slider {
		background-color: var(--color-accent);
	}

	input:focus + .slider {
		box-shadow: 0 0 1px var(--color-accent);
	}

	input:checked + .slider:before {
		-webkit-transform: translateX(26px);
		-ms-transform: translateX(26px);
		transform: translateX(26px);
	}

	/* Rounded sliders */
	.slider.round {
		border-radius: 34px;
	}

	.slider.round:before {
	border-radius: 50%;
	}
</style>
