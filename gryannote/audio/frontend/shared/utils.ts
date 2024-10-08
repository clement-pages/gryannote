import type WaveSurfer from "@gryannote/wavesurfer.js";
import type { WaveSurferOptions } from "@gryannote/wavesurfer.js";
import { audioBufferToWav } from "./audioBufferToWav";

export interface LoadedParams {
	autoplay?: boolean;
}

export function blob_to_data_url(blob: Blob): Promise<string> {
	return new Promise((fulfill, reject) => {
		let reader = new FileReader();
		reader.onerror = reject;
		reader.onload = () => fulfill(reader.result as string);
		reader.readAsDataURL(blob);
	});
}

export const process_audio = async (
	audioBuffer: AudioBuffer,
	start?: number,
	end?: number
): Promise<Uint8Array> => {
	const audioContext = new AudioContext();
	const numberOfChannels = audioBuffer.numberOfChannels;
	const sampleRate = audioBuffer.sampleRate;

	let trimmedLength = audioBuffer.length;
	let startOffset = 0;

	if (start && end) {
		startOffset = Math.round(start * sampleRate);
		const endOffset = Math.round(end * sampleRate);
		trimmedLength = endOffset - startOffset;
	}

	const trimmedAudioBuffer = audioContext.createBuffer(
		numberOfChannels,
		trimmedLength,
		sampleRate
	);

	for (let channel = 0; channel < numberOfChannels; channel++) {
		const channelData = audioBuffer.getChannelData(channel);
		const trimmedData = trimmedAudioBuffer.getChannelData(channel);
		for (let i = 0; i < trimmedLength; i++) {
			trimmedData[i] = channelData[startOffset + i];
		}
	}

	return audioBufferToWav(trimmedAudioBuffer);
};

export function loaded(
	node: HTMLAudioElement,
	{ autoplay }: LoadedParams = {}
): void {
	async function handle_playback(): Promise<void> {
		if (!autoplay) return;
		node.pause();
		await node.play();
	}
}

export const skip_audio = (waveform: WaveSurfer, amount: number): void => {
	if (!waveform) return;
	waveform.skip(amount);
};

export const get_skip_rewind_amount = (
	audio_duration: number,
	skip_length?: number | null
): number => {
	if (!skip_length) {
		skip_length = 5;
	}
	return (audio_duration / 100) * skip_length || 5;
};

export function renderLineWaveform(
    channelData: Array<Float32Array | number[]>,
    ctx: CanvasRenderingContext2D,
    vScale?: number,
  ) {

	vScale = vScale || 1;

    const drawChannel = (index: number) => {
      const channel = channelData[index] || channelData[0];
      const length = channel.length;
      const { height } = ctx.canvas;
      const halfHeight = height / 2;
      const hScale = ctx.canvas.width / length;

      ctx.moveTo(0, halfHeight);

      let prevX = 0;
      let max = 0;
      for (let i = 0; i <= length; i++) {
        const x = Math.round(i * hScale);

        if (x > prevX) {
          const h = Math.round(max * halfHeight * vScale) || 1;
          const y = halfHeight + h * (index === 0 ? -1 : 1);
          ctx.lineTo(prevX, y);
          prevX = x;
          max = 0;
        }

        const value = Math.abs(channel[i] || 0);
        if (value > max) max = value;
      }

      ctx.lineTo(prevX, halfHeight);
    }

    ctx.beginPath();

    drawChannel(0);
    drawChannel(1);
    ctx.fill();
    ctx.closePath();
  }
