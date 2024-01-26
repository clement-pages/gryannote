import os

import gradio as gr
from gradio_annotatedaudio import AnnotatedAudio, Region
from gradio.components import Audio
from pyannote.audio import Pipeline

example = AnnotatedAudio().example_inputs()

def get_diarization(filepath: str):
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=os.environ["HG_TOKEN"])
    print("filepath", filepath)
    dia_outputs = pipeline(filepath)
    speech_turns = []
    for speech_turn, _, speaker in dia_outputs.itertracks(yield_label=True):
        speech_turns.append(Region(
            start=speech_turn.start,
            end=speech_turn.end,
            speaker=speaker,
        ))
    return (filepath, speech_turns)

demo = gr.Interface(
    get_diarization,
    Audio(type="filepath"),  # interactive version of your component
    AnnotatedAudio(),  # static version of your component
    # examples=[[example]],  # uncomment this line to view the "example version" of your component
)


if __name__ == "__main__":
    demo.launch()
