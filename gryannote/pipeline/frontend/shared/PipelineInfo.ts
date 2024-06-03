export default class PipelineInfo {
  name: string;
  token?: string;
  param_specs?: Object;

  constructor({
    name,
    token,
    param_specs,
  }: {
    name: string;
    token?: string;
    param_specs?: Object;
  }) {
    this.name = name;
    this.token = token;
    this.param_specs = param_specs ? param_specs : new Object();
  }
}
