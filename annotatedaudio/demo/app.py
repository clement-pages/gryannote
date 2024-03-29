import gradio as gr
from gradio_annotatedaudio import AnnotatedAudio
from gradio_pipelineselector import PipelineSelector
from pyannote.audio import Pipeline

example = AnnotatedAudio().example_inputs()

annotated_audio = AnnotatedAudio(type="filepath", interactive=True)


def apply_pipeline(pipeline: Pipeline, audio):
    """ Apply specified pipeline on the indicated audio file"""
    annotations = pipeline(audio)

    return (audio, annotations)


def update_annotations(data):
    print(data)


with gr.Blocks() as demo:
    gr.Markdown(
        "Welcome to the [pyannote.audio](https://github.com/pyannote/pyannote-audio) app !"
    )
    pipeline_selector = PipelineSelector(source="dropdown")
    annotated_audio = AnnotatedAudio(
        type="filepath",
        interactive=True,
    )
    annotated_audio.edit(fn=update_annotations, inputs=annotated_audio, preprocess=False)

    run_btn = gr.Button("Run pipeline")
    run_btn.click(
        fn=apply_pipeline,
        inputs=[pipeline_selector, annotated_audio],
        outputs=annotated_audio,
    )


if __name__ == "__main__":
    demo.launch()
