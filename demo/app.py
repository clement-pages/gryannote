import os

import gradio as gr
from gradio.components import Audio
from gradio_annotatedaudio import AnnotatedAudio, Annotation

from pyannote.audio import Pipeline

example = AnnotatedAudio().example_inputs()

def get_diarization(filepath: str):
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=os.environ["HG_TOKEN"])
    print("filepath", filepath)
    dia_outputs = pipeline(filepath)
    annotations = []
    for speech_turn, _, speaker in dia_outputs.itertracks(yield_label=True):
        annotations.append(Annotation(
            start=speech_turn.start,
            end=speech_turn.end,
            speaker=speaker,
        ))
    return (filepath, annotations)

annotated_audio = AnnotatedAudio(interactive=False)

demo = gr.Interface(
    get_diarization,
    inputs=Audio(type="filepath"),
    outputs=annotated_audio,
    # examples=[[example]],  # uncomment this line to view the "example version" of your component
)


if __name__ == "__main__":
    demo.launch()
