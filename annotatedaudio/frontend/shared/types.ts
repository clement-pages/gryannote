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
	level?: number | undefined
	numLevels?: number | undefined
}

export type CaptionLabel = {
	speaker: string
	color: string
	shortcut: string
}
