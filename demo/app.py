import os
import gradio as gr
from pathlib import Path
from gradio_annotatedaudio import AnnotatedAudio

from pyannote.audio import Pipeline

example = AnnotatedAudio().example_inputs()

def get_diarization(filepath: str):
    filepath = Path(filepath)
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=os.environ["HG_TOKEN"])
    annotations = pipeline(filepath)

    return (filepath, annotations)

annotated_audio = AnnotatedAudio(type="filepath", interactive=True)

demo = gr.Interface(
    get_diarization,
    inputs=annotated_audio,
    outputs=annotated_audio,
    # examples=[[example]],  # uncomment this line to view the "example version" of your component
)


if __name__ == "__main__":
    demo.launch()
