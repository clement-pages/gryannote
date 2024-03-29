export default class PipelineInfo {
	name: string;
	token?: string;
        param_specs?: Map<string, any>;

	constructor({
        name,
        token,
        param_specs,
	}: {
        name: string,
        token?: string;
        param_specs?: Map<string, any>
	}) {
        this.name = name;
        this.token = token;
        this.param_specs = new Map(param_specs)
	}
}
