import os

import gradio as gr
from gradio.components import Audio
from pathlib import Path
from gradio_annotatedaudio import AnnotatedAudio, Annotation

from pyannote.audio import Pipeline

example = AnnotatedAudio().example_inputs()

def get_diarization(filepath: str):
    filepath = Path(filepath)
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=os.environ["HG_TOKEN"])
    dia_outputs = pipeline(filepath)
    # write rttm into same repo as audio file:
    rttm_path = filepath.parent.absolute() / Path("results.rttm")
    with open(rttm_path, "w") as rttm_file:
        dia_outputs.write_rttm(rttm_file)

    annotations = []
    for speech_turn, _, speaker in dia_outputs.itertracks(yield_label=True):
        annotations.append(Annotation(
            start=speech_turn.start,
            end=speech_turn.end,
            speaker=speaker,
        ))
    return (filepath, rttm_path, annotations)

annotated_audio = AnnotatedAudio(type="filepath", interactive=True)

demo = gr.Interface(
    get_diarization,
    inputs=annotated_audio,
    outputs=annotated_audio,
    # examples=[[example]],  # uncomment this line to view the "example version" of your component
)


if __name__ == "__main__":
    demo.launch()
