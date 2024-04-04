import gradio as gr
from gradio_pipelineselector import PipelineSelector

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
