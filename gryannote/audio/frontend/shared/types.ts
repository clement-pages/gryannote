export type WaveformOptions = {
	waveform_color?: string;
	waveform_progress_color?: string;
	show_controls?: boolean;
	skip_length?: number;
	trim_region_color?: string;
	show_recording_waveform?: boolean;
};

export type Annotation = {
	start: number
	end: number
	speaker: string
}

export type Label = {
	name: string
	color: string
	shortcut: string
}

export type AxeEvent = {idx:number, value:number}
export type ButtonEvent = {idx: number}
