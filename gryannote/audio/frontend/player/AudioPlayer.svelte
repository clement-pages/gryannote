<script lang="ts">
	import type { HoverOptions, TimelineOptions, WaveformOptions } from "../shared/types";
	import type { I18nFormatter } from "@gradio/utils";
	import { Music,} from "@gradio/icons";
	import WaveSurfer from "@gryannote/wavesurfer.js";
	import GamepadPlugin from "@gryannote/wavesurfer.js/dist/plugins/gamepad.js";
	import MiniMapPlugin from "@gryannote/wavesurfer.js/dist/plugins/minimap.js";
	import TimelinePlugin from '@gryannote/wavesurfer.js/dist/plugins/timeline.js';
	import HoverPlugin from '@gryannote/wavesurfer.js/dist/plugins/hover.js';
	import WaveformControls from "../shared/WaveformControls.svelte";
	import Caption from "./Caption.svelte";
	import RegionsControl from "./RegionsControl.svelte";
	import { Empty } from "@gradio/atoms";
	import { resolve_wasm_src } from "@gradio/wasm/svelte";
	import AnnotatedAudioData from "../shared/AnnotatedAudioData";
	import { createEventDispatcher } from "svelte";
	import { renderLineWaveform } from "../shared/utils";

	export let label: string;
	export let i18n: I18nFormatter;
	export let value: AnnotatedAudioData | null = null;
	export let interactive = true;
	export let show_minimap: boolean = true;
	export let waveform_settings: Record<string, any>;
	export let waveform_options: WaveformOptions;
	export let timeline_options: TimelineOptions;
	export let hover_options: HoverOptions;
	export let isDialogOpen: boolean;
	export let mode: string = "";

	let container: HTMLDivElement;
	let waveform: WaveSurfer | undefined;
	let wsGamepad: GamepadPlugin;
	let wsTimeline: TimelinePlugin;
	let wsHover: HoverPlugin;
	let wsMinimap: MiniMapPlugin;

	let timeRef: HTMLTimeElement;
	let durationRef: HTMLTimeElement;
	let audio_duration: number;

	let caption: Caption;

	let regionsControl: RegionsControl;

	const dispatch = createEventDispatcher<{
		stop: undefined;
		play: undefined;
		pause: undefined;
		timeupdate: number;
		edit: typeof value;
	}>();

	function formatTime(seconds: number): string {
		const minutes = Math.floor(seconds / 60);
		const secondsRemainder = Math.round(seconds) % 60;
		const paddedSeconds = `0${secondsRemainder}`.slice(-2);
		return `${minutes}:${paddedSeconds}`;
	};

	function create_waveform(): void {
		waveform = WaveSurfer.create({
			container: container,
			...waveform_settings
		});
		resolve_wasm_src(value.file_data?.url).then((resolved_src) => {
			if (resolved_src && waveform) {
				return waveform.load(resolved_src);
			}
		});
	}

	/**
	 * Adjust position of the cursor on the waveform
	 * @param key shortcut name. Indicates direction: forward or backward.
	 * @param shiftKey indicates whether shift key was pressed. If true, move faster
	 */
	 function adjustTimeCursorPosition(key: string, shiftKey: boolean): void {
		let currentTime = waveform.getCurrentTime();
		let newTime: number;
		let delta = 0.05; //TODO do not hardcore this and adapt it according to relative size of the waveform

		// if alt is pressed, go faster
		if(shiftKey){
			delta = delta * 4.0;
		}

		if(key === "ArrowLeft"){
			newTime = currentTime - delta;
		}else {
			newTime = currentTime + delta;
		}

		waveform.setTime(newTime);
	}

	$: if (container) {
		if (waveform) waveform.destroy();
		container.innerHTML = "";
		create_waveform();
	}

	$: waveform?.on("decode", (duration: any) => {
		audio_duration = duration;
		durationRef && (durationRef.textContent = formatTime(duration));
	});

	$: waveform?.on(
		"timeupdate",
		(currentTime: number) =>{
			timeRef && (timeRef.textContent = formatTime(currentTime));
			// avoid submerging event listerners when audio is played
			if(!waveform.isPlaying()) dispatch("timeupdate", currentTime);
		}
	);

	$: waveform?.on("ready", () => {
		if(!wsGamepad){
			wsGamepad = waveform.registerPlugin(GamepadPlugin.create());
		}

		if(!wsTimeline){
			wsTimeline = waveform.registerPlugin(TimelinePlugin.create({
				formatTimeCallback: formatTime,
				...timeline_options,
			}));
		}

		if(!wsHover){
			wsHover = waveform.registerPlugin(HoverPlugin.create({
				// cast seconds to a string with 10e-3 precision
				formatTimeCallback: (seconds: number) => seconds.toFixed(3),
				...hover_options,
			}));
		}

		if(show_minimap && !wsMinimap){
			wsMinimap = waveform.registerPlugin(MiniMapPlugin.create({
				waveColor: waveform_options.waveform_color,
            	progressColor: waveform_options.waveform_color,
				insertPosition: "beforebegin",
				height: 30,
			}));

			wsMinimap.on("init", () => {
				const miniWaveform = wsMinimap.getWaveform();
				miniWaveform.setOptions({
					renderFunction: (peaks, ctx) => {
						// render mini waveform
						renderLineWaveform(peaks, ctx);

						// color waveform according to region's color:
						ctx.globalCompositeOperation = "source-atop";
						const pxPerSecond = miniWaveform.getWidth() / miniWaveform.getDuration();
						regionsControl.getRegions().forEach(region => {
							ctx.fillStyle = region.color.substring(0, 7);
							ctx.fillRect(region.start * pxPerSecond, 0, (region.end -region.start) * pxPerSecond, 30);
						});
					}
				});
			});
		}
	});

	async function load_audio(data: string): Promise<void> {
		await resolve_wasm_src(data).then((resolved_src) => {
			if (!resolved_src || value.file_data?.is_stream) return;
			return waveform?.load(resolved_src);
		});
	}

	$: url = value.file_data?.url;
	$: url && load_audio(url);

</script>

{#if value === null}
	<Empty size="small">
		<Music />
	</Empty>
{:else if value.file_data.is_stream}
	<audio
		class="standard-player"
		src={value.file_data.url}
		controls
		autoplay={waveform_settings.autoplay}
	/>
{:else}
	<div
		class="component-wrapper"
		data-testid={label ? "waveform-" + label : "unlabelled-audio"}
	>
		<div class="waveform-container">
			<div id="waveform" bind:this={container} />
		</div>

		<div class="timestamps">
			<time bind:this={timeRef} id="time">0:00</time>
			<div>
				<time bind:this={durationRef} id="duration">0:00</time>
			</div>
		</div>

		{#if waveform}
			<div class="commands">
				<div class="waveform-controls">
					<WaveformControls
						{isDialogOpen}
						{waveform}
						{wsGamepad}
						{audio_duration}
						{i18n}
						{waveform_options}
						on:play={() => dispatch("play")}
						on:stop={() => dispatch("stop")}
						on:pause={() => dispatch("pause")}
					/>
				</div>
				<div class="regions-controls">
					<RegionsControl
						bind:this={regionsControl}
						bind:mode
						bind:isDialogOpen
						{adjustTimeCursorPosition}
						{waveform}
						{caption}
						{wsGamepad}
						{i18n}
						{value}
						on:edit={(e) => {
							if(wsMinimap){
								// force mini-map to be redraw with updated regions
								wsMinimap.getWaveform().setOptions({});
							}
							dispatch("edit", e.detail)
						}}
					/>

				</div>
			</div>
			{#if value}
				<Caption
					bind:this={caption}
					bind:isDialogOpen
					{interactive}
					{wsGamepad}
					on:select={(e) => {
						regionsControl.setRegionLabel(e.detail)
					}}
					on:name_update={(e) => {
						regionsControl.getRegions().forEach(region => {
							if(region.color === e.detail.color){
								regionsControl.setRegionLabel(e.detail, region);
							}
						});
					}}
					on:color_update={(e) => {
						// update all regions associated with the modified label
						regionsControl.getRegions().forEach(region => {
							if(regionsControl.getRegionLabel(region.id) === e.detail.name){
								regionsControl.setRegionLabel(e.detail, region);
							}
						});
					}}
				/>
			{/if}
		{/if}
	</div>
{/if}

<style>
	.commands {
		display: flex;
		justify-content: space-between;
	}

	.component-wrapper {
		padding: 0.5em 4em 4em;
	}

	:global(::part(wrapper)) {
			margin-bottom: var(--size-2);
	}

	:global(::part(minimap)){
		margin-bottom: 0.5em;
	}

	.timestamps {
		display: flex;
		justify-content: space-between;
		align-items: center;
		width: 100%;
		padding: var(--size-1) 0;
	}

	#time {
		color: var(--neutral-400);
	}

	#duration {
		color: var(--neutral-400);
	}

	.waveform-container {
		display: flex;
		align-items: center;
		justify-content: center;
		width: var(--size-full);
	}

	.waveform-controls {
		width: 80em;
	}

	#waveform {
		width: 100%;
		height: 100%;
		position: relative;
	}

	.standard-player {
		width: 100%;
		padding: var(--size-2);
	}
</style>
