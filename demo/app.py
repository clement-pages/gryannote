
import gradio as gr
from gradio_annotatedaudio import AnnotatedAudio


with gr.Blocks() as demo:
    gr.Markdown("# Change the value (keep it JSON) and the front-end will update automatically.")
    AnnotatedAudio(value={"message": "Hello from Gradio!"}, label="Static")


demo.launch()
