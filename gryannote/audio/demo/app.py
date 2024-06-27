import gradio as gr
from gryannote_audio import AudioLabeling
from pyannote.audio import Pipeline

audio_labeling = AudioLabeling(type="filepath", interactive=True)


def apply_pipeline(audio):
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1")
    annotations = pipeline(audio)
    return (audio, annotations)


demo = gr.Interface(apply_pipeline, inputs=audio_labeling, outputs=audio_labeling)


if __name__ == "__main__":
    demo.launch()
