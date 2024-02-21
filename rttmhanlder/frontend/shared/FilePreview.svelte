<script lang="ts">
	import type { FileData } from "@gradio/client";
	import { createEventDispatcher } from "svelte";
	import type { I18nFormatter, SelectData } from "@gradio/utils";
	import IconButton from "@gradio/atoms/src/IconButton.svelte";
	import { Download } from "@gradio/icons";

	const dispatch = createEventDispatcher<{
		select: SelectData;
	}>();
	export let value: FileData | FileData[];
	export let selectable = false;
	export let height: number | undefined = undefined;
	export let i18n: I18nFormatter;

	function splitFilename(filename: string): [string, string] {
		const last_dot = filename.lastIndexOf(".");
		if (last_dot === -1) {
			return [filename, ""];
		}
		return [filename.slice(0, last_dot), filename.slice(last_dot)];
	}

	function getFileContent(fileUrl: string, id: string) {
		fetch(fileUrl)
			.then(response => response.text())
			.then(content => {
				document.getElementById(id).innerText = content;
			})
			.catch(error => console.error("Error while fetching file:", error))
	}

	$: normalized_files = (Array.isArray(value) ? value : [value]).map((file) => {
		const [filename_stem, filename_ext] = splitFilename(file.orig_name ?? "");
		return {
			...file,
			filename_stem,
			filename_ext
		};
	});
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
							<button>
								<a href={file.url} target="_blank" download={file.orig_name}>
									<IconButton Icon={Download}/>
								</a>
							</button>
						{:else}
							{i18n("file.uploading")}
						{/if}
					</td>
				</tr>
				<!-- File content -->
				<tr class="file-content" id="file-content-{i}">
					<td>
						{#if file.url}
							{console.log("Passing here")}
							{getFileContent(file.url, "file-content-" + i.toString())}
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

	.selectable {
		cursor: pointer;
	}



	tbody > tr:nth-child(even) {
		background: var(--block-background-fill);
	}

	tbody > tr:nth-child(odd) {
		background: var(--table-odd-background-fill);
	}
</style>
