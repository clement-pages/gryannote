<script lang="ts">
	import { onMount } from "svelte";
	import { Block } from "@gradio/atoms";
	import { StatusTracker } from "@gradio/statustracker";
	import type { LoadingStatus } from "@gradio/statustracker";
	import type { SelectData, Gradio } from "@gradio/utils";
	import type { FileData} from "@gradio/client";
	import { Upload, ModifyUpload} from "@gradio/upload";
	import PipelineConfig from "./shared/PipelineConfig";
	import { listModels, listFiles, downloadFile } from "@huggingface/hub";
	import type { RepoDesignation, Credentials } from "@huggingface/hub";
	import text2Yaml from "./shared/yamlReader";


	export let elem_id = "";
	export let elem_classes: string[] = [];
	export let visible = true;
	export let value: PipelineConfig | null = null;
	export let available_pipelines: string[] = [];
	export let container = true;
	export let scale: number | null = null;
	export let min_width: number | undefined = undefined;
	export let loading_status: LoadingStatus;
	export let dragging: boolean;
	export let root: string;

	export let gradio: Gradio<{
		change: never;
		error: string;
		warning: string;
		select: string;
		upload: PipelineConfig;
		input: never;
	}>;

	function handleLoad({detail}: {detail : FileData}): void {
		value = new PipelineConfig(detail);
		gradio.dispatch("upload", value);
	}



	function handleError({ detail }: CustomEvent<string>): void {
		const [level, status] = detail.includes("Invalid file type")
			? ["warning", "complete"]
			: ["error", "error"];
		loading_status = loading_status || {};
		loading_status.status = status as LoadingStatus["status"];
		loading_status.message = detail;
		gradio.dispatch(level as "error" | "warning", detail);
	}

	onMount(async () =>  {
		for await (const model of listModels({search: {tags: ["pyannote-audio-pipeline"]}})){
			if(model.name.startsWith("pyannote/")){
				available_pipelines = [...available_pipelines, model.name];
			}
		}
		let repo: RepoDesignation = { type: "model", name: available_pipelines[0]};
		const credentials: Credentials = { accessToken: "..."};
		let config_text = await (await downloadFile({repo, credentials, path: "config.yaml"})).text();
		console.log(text2Yaml(config_text));
		// add form event listeners
		document.getElementById("pipeline-name").addEventListener("select", (): void => {
			gradio.dispatch("select", this.value);
		})
	});

</script>

<Block {visible} {elem_id} {elem_classes} {container} {scale} {min_width}>
	{#if loading_status}
		<StatusTracker
			autoscroll={gradio.autoscroll}
			i18n={gradio.i18n}
			{...loading_status}
		/>
	{/if}
	{#if value === null}
		<Upload
			filetype="text/*"
			on:load={handleLoad}
			on:error={handleError}
			bind:dragging
			{root}
		>
			Upload your config file
		</Upload>
		
		<form action="">
			<label for="pipeline-name"> Select a pipeline from the list</label>
			<select name="pipeline-name" id="pipeline-name">
				{#each available_pipelines as pipeline }
					<option value={pipeline}> {pipeline} </option>
				{/each}
			</select>
		</form>
	{/if}

</Block>
