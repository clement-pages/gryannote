import gradio as gr
from gryannote_pipeline import PipelineSelector

with gr.Blocks() as demo:
    pipeline_selector = PipelineSelector(
        show_config=True, default_pipeline="pyannote/speaker-diarization-3.1"
    )

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
