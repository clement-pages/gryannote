import {FileData} from "@gradio/client"


export default class PipelineConfig {
    config: FileData | string;
    auth_token?: string | null;

    constructor(config: FileData | string, auth_token: string | null = null){
        this.config = config;
        this.auth_token = auth_token
    }
}
