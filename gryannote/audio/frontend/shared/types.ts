export type WaveformOptions = {
	waveform_color?: string;
	waveform_progress_color?: string;
	show_controls?: boolean;
	skip_length?: number;
	trim_region_color?: string;
	show_recording_waveform?: boolean;
};

export type TimelineOptions = {
	height?: number
	nsertPosition?: InsertPosition
	primaryLabelInterval?: number
	primaryLabelSpacing?: number,
	secondaryLabelInterval?: number,
	secondaryLabelOpacity?: number,
	secondaryLabelSpacing?: number,
	timeInterval?: number
}

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
