export default class PipelineInfo {
	name: string;
	token?: string;

	constructor({
        name,
        token,
	}: {
        name: string,
        token?: string;
	}) {
        this.name = name;
        this.token = token;
	}
}
