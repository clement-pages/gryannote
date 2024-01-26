import type { FileData } from "@gradio/client";

export type WaveformOptions = {
	waveform_color?: string;
	waveform_progress_color?: string;
	show_controls?: boolean;
	skip_length?: number;
	trim_region_color?: string;
	show_recording_waveform?: boolean;
};

export type Region = {
	start: Number
	end: Number
	speaker: string
	color: string
}

export type AudioData = {
    file_data: FileData
    regions?: Region[]
}
