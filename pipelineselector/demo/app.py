import os

import gradio as gr
from gradio_pipelineselector import PipelineSelector
from pyannote.audio import Pipeline

example = PipelineSelector().example_inputs()

pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1", use_auth_token=os.environ["HG_TOKEN"]
)

with gr.Blocks() as demo:
    pipeline_selector = PipelineSelector()

    pipeline_selector.select(
        fn=pipeline_selector.on_select,
        inputs=pipeline_selector,
        outputs=pipeline_selector,
        preprocess=False,
        postprocess=False,
    )

    pipeline_selector.change(
        fn=pipeline_selector.on_change,
        inputs=pipeline_selector,
        outputs=pipeline_selector,
        preprocess=False,
        postprocess=False,
    )

if __name__ == "__main__":
    demo.launch()
