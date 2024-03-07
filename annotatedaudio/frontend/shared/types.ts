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
	color: string
	level: number
	numLevels: number
}

export type CaptionItem = {
	speaker: string
	color: string
	shortcut: string
}
