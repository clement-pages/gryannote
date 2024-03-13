
import gradio as gr
from gradio_pipelinehandler import PipelineHandler


with gr.Blocks() as demo:
    gr.Markdown("# Load a configuration file or select a pipeline in the dropdown list")
    pipeline_handler = PipelineHandler()
    pipeline_handler.select(pipeline_handler.get_pipeline_params)


if __name__ == "__main__":
    demo.launch()
