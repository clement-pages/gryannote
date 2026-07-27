"""Patch gradio_client/utils.py to handle boolean additionalProperties.

Fixes TypeError in gradio_client==1.7.2 where additionalProperties: true
(a boolean) is passed to _json_schema_to_python_type which expects a dict.
This was fixed upstream in gradio_client>=1.8.0.
"""
import site
import os

for search_path in site.getsitepackages() + [site.getusersitepackages()]:
    target = os.path.join(search_path, "gradio_client", "utils.py")
    if os.path.exists(target):
        with open(target, "r") as f:
            content = f.read()

        old = '''        if "additionalProperties" in schema:
            des += [
                f"str, {_json_schema_to_python_type(schema['additionalProperties'], defs)}"
            ]'''

        new = '''        if "additionalProperties" in schema:
            additional_properties = schema["additionalProperties"]
            if isinstance(additional_properties, bool) and additional_properties:
                des += ["str, Any"]
            else:
                des += [
                    f"str, {_json_schema_to_python_type(additional_properties, defs)}"
                ]'''

        if old in content:
            content = content.replace(old, new)
            with open(target, "w") as f:
                f.write(content)
            print(f"Patched: {target}")
            break
        else:
            print(f"Already patched or pattern not found: {target}")
            break
else:
    print("gradio_client/utils.py not found")
