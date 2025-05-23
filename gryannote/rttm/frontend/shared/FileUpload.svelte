<script lang="ts">
	import { createEventDispatcher, tick } from "svelte";
	import { Upload, ModifyUpload } from "@gradio/upload";
	import { FileData, type Client } from "@gradio/client";
	import { BlockLabel } from "@gradio/atoms";
	import { File } from "@gradio/icons";

	import FilePreview from "./FilePreview.svelte";
	import type { I18nFormatter } from "@gradio/utils";

	export let value: FileData | FileData[] | null;

	export let label: string;
	export let show_label = true;
	export let file_count: "single" | "multiple" | "directory" = "single";
	export let file_types: string[] | null = null;
	export let selectable = false;
	export let root: string;
	export let height: number | undefined = undefined;
	export let i18n: I18nFormatter;
	export let max_file_size: number | null = null;
	export let upload: Client["upload"];
	export let stream_handler: Client["stream"];

	async function handle_upload({
		detail
	}: CustomEvent<FileData | FileData[]>): Promise<void> {
		value = detail;
		await tick();
		dispatch("change", value);
		dispatch("upload", detail);
	}

	function handle_clear(): void {
		value = null;
		dispatch("change", null);
		dispatch("clear");
	}

	const dispatch = createEventDispatcher<{
		change: FileData[] | FileData | null;
		clear: undefined;
		drag: boolean;
		upload: FileData[] | FileData;
		load: FileData[] | FileData;
		error: string;
	}>();

	let accept_file_types: string | null;
	if (file_types == null) {
		accept_file_types = null;
	} else {
		file_types = file_types.map((x) => {
			if (x.startsWith(".")) {
				return x;
			}
			return x + "/*";
		});
		accept_file_types = file_types.join(", ");
	}

	let dragging = false;
	$: dispatch("drag", dragging);
</script>

<BlockLabel
	{show_label}
	Icon={File}
	float={value === null}
	label={label || "File"}
/>

{#if value}
	<ModifyUpload {i18n} on:clear={handle_clear} absolute />
	<FilePreview {i18n} on:select {selectable} {value} {height} />
{:else}
	<Upload
		on:load={handle_upload}
		filetype={accept_file_types}
		{file_count}
		{root}
		{max_file_size}
		{upload}
		{stream_handler}
		bind:dragging
	>
		<slot />
	</Upload>
{/if}
