import {FileData} from "@gradio/client"
import type {Annotation} from "./types.ts"


export default class AnnotatedAudioData {
	file_data: FileData;
	annotations?: Annotation[] | null;


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
	}) {
		this.file_data = new FileData({path, url, orig_name, size, blob, is_stream, mime_type, alt_text})
		this.annotations = null;
	}
}