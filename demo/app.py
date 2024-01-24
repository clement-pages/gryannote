
import gradio as gr
from gradio_annotatedaudio import AnnotatedAudio


example = AnnotatedAudio().example_inputs()

demo = gr.Interface(
    lambda x:x,
    AnnotatedAudio(),  # interactive version of your component
    AnnotatedAudio(),  # static version of your component
    # examples=[[example]],  # uncomment this line to view the "example version" of your component
)


if __name__ == "__main__":
    demo.launch()
