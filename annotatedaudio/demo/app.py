import os
from typing import List

import gradio as gr
from gradio_annotatedaudio import AnnotatedAudio
from pyannote.audio import Pipeline

example = AnnotatedAudio().example_inputs()
annotated_audio = AnnotatedAudio(type="filepath", interactive=True)


def get_available_pipelines() -> List[str]:
    """ Get pipelines list, sorted according to the
    order in which they were last modified"""
    from huggingface_hub import HfApi

    available_pipelines = [
        p.modelId for p in HfApi().list_models(filter="pyannote-audio-pipeline", sort="last_modified", direction=-1)
    ]
    return list(filter(lambda p: p.startswith("pyannote/"), available_pipelines))


def apply_pipeline(pipeline_name: str, data: AnnotatedAudio):
    """ Apply specified pipeline on the indicated file"""
    filepath, _ = data
    pipeline = Pipeline.from_pretrained(
        pipeline_name, use_auth_token=os.environ["HG_TOKEN"]
    )
    annotations = pipeline(filepath)

    return (filepath, annotations)


def update_annotations(data: AnnotatedAudio):
    print(data)


with gr.Blocks() as demo:
    gr.Markdown(
        "Welcome to the [pyannote.audio](https://github.com/pyannote/pyannote-audio) app !"
    )
    pipelines = get_available_pipelines()
    pipelines_choice = gr.Dropdown(
        choices=pipelines,
        label="Choose one pipeline to apply:",
        value=pipelines[0],
        interactive=True,
    )

    annotated_audio = AnnotatedAudio(
        type="filepath",
        interactive=True,
    )
    annotated_audio.edit(fn=update_annotations, inputs=annotated_audio)

    run_btn = gr.Button("Run pipeline")
    run_btn.click(
        fn=apply_pipeline,
        inputs=[pipelines_choice, annotated_audio],
        outputs=annotated_audio,
    )


if __name__ == "__main__":
    demo.launch()
