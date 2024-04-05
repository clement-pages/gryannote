import gradio as gr
from gradio_annotatedaudio import AnnotatedAudio
from gradio_pipelineselector import PipelineSelector
from pyannote.audio import Pipeline

example = AnnotatedAudio().example_inputs()

annotated_audio = AnnotatedAudio(type="filepath", interactive=True)


def get_annotations():
    audio = ...
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1")
    annotations = pipeline(audio)
    return (audio, annotations)


value = get_annotations()


def apply_pipeline(pipeline: Pipeline, audio):
    """Apply specified pipeline on the indicated audio file"""
    annotations = pipeline(audio)

    return (audio, annotations)


with gr.Blocks() as demo:
    gr.Markdown(
        "Welcome to the [pyannote.audio](https://github.com/pyannote/pyannote-audio) app !"
    )
    pipeline_selector = PipelineSelector()
    pipeline_selector.select(
        fn=pipeline_selector.on_select,
        inputs=pipeline_selector,
        outputs=pipeline_selector,
        preprocess=False,
        postprocess=False,
    )
    pipeline_selector.change(
        fn=pipeline_selector.on_change,
        inputs=pipeline_selector,
        outputs=pipeline_selector,
        preprocess=False,
        postprocess=False,
    )

    annotated_audio = AnnotatedAudio(
        type="filepath",
        # value=value,
        interactive=True,
    )

    run_btn = gr.Button("Run pipeline")
    run_btn.click(
        fn=apply_pipeline,
        inputs=[pipeline_selector, annotated_audio],
        outputs=annotated_audio,
    )


if __name__ == "__main__":
    demo.launch()
