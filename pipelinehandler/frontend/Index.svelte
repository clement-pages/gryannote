<script lang="ts">
	import { Block } from "@gradio/atoms";
	import { StatusTracker } from "@gradio/statustracker";
	import type { LoadingStatus } from "@gradio/statustracker";
	import type { SelectData, Gradio } from "@gradio/utils";
	import type { FileData} from "@gradio/client"
	import { Upload, ModifyUpload} from "@gradio/upload"
	import PipelineConfig from "./shared/PipelineConfig"


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
		select: SelectData;
		upload: PipelineConfig;
		input: never;
	}>;

	function handleLoad({detail}: {detail : FileData}): void {
		value = new PipelineConfig(detail);
		gradio.dispatch("upload", value);
	}

	$: console.log(value);


	function handleError({ detail }: CustomEvent<string>): void {
		const [level, status] = detail.includes("Invalid file type")
			? ["warning", "complete"]
			: ["error", "error"];
		loading_status = loading_status || {};
		loading_status.status = status as LoadingStatus["status"];
		loading_status.message = detail;
		gradio.dispatch(level as "error" | "warning", detail);
	}

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
			<slot/>
		</Upload>
		<select>
			<option value="A"> Test1 </option>
			<option value="B"> Test2 </option>
		</select>
	{/if}

</Block>
