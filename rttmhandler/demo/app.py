import os
from typing import List

import gradio as gr
from gradio_annotatedaudio import AnnotatedAudio
from gradio_rttmhandler import RTTMHandler
from pyannote.audio.core.pipeline import Pipeline


def get_available_pipelines() -> List[str]:
    """Get pipelines list, sorted according to the
    order in which they were last modified"""
    from huggingface_hub import HfApi

    available_pipelines = [
        p.modelId
        for p in HfApi().list_models(
            filter="pyannote-audio-pipeline", sort="last_modified", direction=-1
        )
    ]
    return list(filter(lambda p: p.startswith("pyannote/"), available_pipelines))


def apply_pipeline(pipeline_name: str, filepath: str):
    """Apply specified pipeline on the indicated file"""
    pipeline = Pipeline.from_pretrained(
        pipeline_name, use_auth_token=os.environ["HG_TOKEN"]
    )
    annotations = pipeline(filepath)

    return ((filepath, annotations), (filepath, annotations))


with gr.Blocks() as demo:
    pipelines = get_available_pipelines()
    pipeline_selector = gr.Dropdown(
        choices=pipelines,
        value=pipelines[0],
        label="Choose the pipeline to apply",
        interactive=True,
    )
    annotated_audio = AnnotatedAudio(type="filepath", interactive=True)
    rttm_handler = RTTMHandler()

    run_btn = gr.Button("Run pipeline")
    run_btn.click(
        fn=apply_pipeline,
        inputs=[pipeline_selector, annotated_audio],
        outputs=[annotated_audio, rttm_handler],
    )
if __name__ == "__main__":
    demo.launch()
