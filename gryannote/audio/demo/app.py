import gradio as gr
from gryannote.audio import AnnotatedAudio
from pyannote.audio import Pipeline

annotated_audio = AnnotatedAudio(type="filepath", interactive=True)


def apply_pipeline(audio):
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1")
    annotations = pipeline(audio)
    return (audio, annotations)

demo = gr.Interface(apply_pipeline, inputs=annotated_audio, outputs=annotated_audio)

demo.launch()
