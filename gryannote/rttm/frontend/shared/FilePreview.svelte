<script lang="ts">
	import type { FileData } from "@gradio/client";
	import {prettyBytes} from "./utils";
	import { createEventDispatcher, onMount, onDestroy } from "svelte";
	import type { I18nFormatter, SelectData } from "@gradio/utils";
	import { DownloadLink } from "@gradio/wasm/svelte";

	const dispatch = createEventDispatcher<{
		select: SelectData;
	}>();
	export let value: FileData | FileData[];
	export let selectable = false;
	export let height: number | undefined = undefined;
	export let i18n: I18nFormatter;

	const MAX_PREVIEW_LINES = 200;
	let fileContentText = "";
	let isLoading = false;
	let lastFetchedUrl = "";
	let lastValueSize = -1;

	function splitFilename(filename: string): [string, string] {
		const last_dot = filename.lastIndexOf(".");
		if (last_dot === -1) {
			return [filename, ""];
		}
		return [filename.slice(0, last_dot), filename.slice(last_dot)];
	}

	function fetchFileContent(fileUrl: string): void {
		isLoading = true;
		lastFetchedUrl = fileUrl;

		fetch(fileUrl, { cache: "no-store" })
			.then(response => response.text())
			.then(content => {
				if (lastFetchedUrl !== fileUrl) return;
				const lines = content.split("\n");
				fileContentText = lines.length > MAX_PREVIEW_LINES
					? lines.slice(0, MAX_PREVIEW_LINES).join("\n") + `\n... (${lines.length - MAX_PREVIEW_LINES} more lines)`
					: content;
				isLoading = false;
			})
			.catch(error => {
				console.error("Error while fetching file:", error);
				if (lastFetchedUrl === fileUrl) isLoading = false;
			});
	}

	function downloadFile() {
		const files = Array.isArray(value) ? value : [value];
		if (files.length > 0 && files[0].url) {
			const a = document.createElement("a");
			a.href = files[0].url;
			a.download = files[0].orig_name ?? "output.rttm";
			document.body.appendChild(a);
			a.click();
			document.body.removeChild(a);
		}
	}

	function onKeydown(e: KeyboardEvent) {
		if ((e.ctrlKey || e.metaKey) && e.key === "s") {
			e.preventDefault();
			downloadFile();
		}
	}

	onMount(() => {
		window.addEventListener("keydown", onKeydown);
	});

	onDestroy(() => {
		window.removeEventListener("keydown", onKeydown);
	});

	$: normalized_files = (Array.isArray(value) ? value : [value]).map((file) => {
		const [filename_stem, filename_ext] = splitFilename(file.orig_name ?? "");
		return {
			...file,
			filename_stem,
			filename_ext
		};
	});

	$: {
		const files = Array.isArray(value) ? value : [value];
		const file = files[0];
		if (file?.url) {
			const currentSize = file.size ?? 0;
			if (file.url !== lastFetchedUrl || currentSize !== lastValueSize) {
				lastValueSize = currentSize;
				fetchFileContent(file.url);
			}
		}
	}

	const is_browser = typeof window !== "undefined";
</script>

<div
	class="file-preview-holder"
	style="max-height: {typeof height === undefined ? 'auto' : height + 'px'};"
>
	<table class="file-preview">
		<tbody>
			{#each normalized_files as file, i}
			<!--File head (name and download button)-->
				<tr
					class="file"
					class:selectable
					on:click={() =>
						dispatch("select", {
							value: file.orig_name,
							index: i
						})}
				>
					<td class="filename" aria-label={file.orig_name}>
						<span class="stem">{file.filename_stem}</span>
						<span class="ext">{file.filename_ext}</span>
					</td>

					<td class="download">
						{#if file.url}
							<DownloadLink
								href={file.url}
								download={is_browser
									? null
									: file.orig_name}
							>
								<span class="save-btn" title="Save RTTM (Ctrl+S)">
									<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
										<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
										<polyline points="7 10 12 15 17 10"/>
										<line x1="12" y1="15" x2="12" y2="3"/>
									</svg>
									Save
								</span>
							</DownloadLink>
						{:else}
							{i18n("file.uploading")}
						{/if}
					</td>
				</tr>
				<!-- File content -->
				<tr class="file-content">
					<td class="file-content-cell">
						{#if isLoading}
							<span class="loading-text">Loading...</span>
						{:else if fileContentText}
							<pre class="rttm-content">{fileContentText}</pre>
						{/if}
					</td>
				</tr>
			{/each}
		</tbody>
	</table>
</div>

<style>
	.file-preview {
		table-layout: fixed;
		width: var(--size-full);
		max-height: var(--size-60);
		overflow-y: auto;
		margin-top: var(--size-1);
		color: var(--body-text-color);
	}

	.file {
		display: flex;
		width: var(--size-full);
	}

	.file > * {
		padding: var(--size-1) var(--size-2-5);
	}

	.filename {
		flex-grow: 1;
		display: flex;
		overflow: hidden;
	}
	.filename .stem {
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}
	.filename .ext {
		white-space: nowrap;
	}

	.download {
		min-width: 8rem;
		width: 10%;
		white-space: nowrap;
		text-align: right;
	}

	.save-btn {
		display: inline-flex;
		align-items: center;
		gap: 4px;
		padding: 2px 8px;
		border: 1px solid var(--neutral-400);
		border-radius: 4px;
		font-size: var(--text-sm);
		color: var(--neutral-400);
		cursor: pointer;
		transition: all 0.15s;
	}

	.save-btn:hover {
		color: var(--color-accent);
		border-color: var(--color-accent);
	}

	.selectable {
		cursor: pointer;
	}



	.file-content-cell {
		width: 100%;
	}

	.rttm-content {
		white-space: pre-wrap;
		word-break: break-all;
		font-family: var(--font-mono);
		font-size: var(--text-sm);
		max-height: 400px;
		overflow-y: auto;
		margin: 0;
		padding: var(--size-2);
	}

	.loading-text {
		color: var(--neutral-400);
		font-size: var(--text-sm);
		padding: var(--size-2);
	}

	tbody > tr:nth-child(even) {
		background: var(--block-background-fill);
	}

	tbody > tr:nth-child(odd) {
		background: var(--table-odd-background-fill);
	}
</style>
