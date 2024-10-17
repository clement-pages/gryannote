import {FileData} from "@gradio/client"
import type {Annotation} from "./types.ts"

const VIDEO_SUPPORTED_FORMAT = ["mp4", "avi"]

export default class AnnotatedAudioData {
	audio: FileData | null = null;
	video: FileData | null = null;
	annotations?: Annotation[] | null = null;


	constructor({
		path,
		url,
		orig_name,
		size,
		blob,
		is_stream,
		mime_type,
		alt_text
	}: {
		path: string;
		url?: string;
		orig_name?: string;
		size?: number;
		blob?: File;
		is_stream?: boolean;
		mime_type?: string;
		alt_text?: string;
	}, annotations?: Annotation[]) {
		const media = new FileData({path, url, orig_name, size, blob, is_stream, mime_type, alt_text});
		const format = media.path.split(".").at(-1);
		console.log(format)
		if(format && VIDEO_SUPPORTED_FORMAT.find(((f) => format == f))){
			this.video = {...media};
		} else {
			this.audio = {...media};
		}

		this.annotations = annotations ? [...annotations] : null;
		console.log(this);
	}
}
