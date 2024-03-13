import fs from "fs"
import yaml from "js-yaml"

export default function text2Yaml(text){
    try {
        const data = yaml.dump(text);
        return data;
    } catch(error){
        console.error("Error reading YAML file: ", error);
        return null;
    }
}
