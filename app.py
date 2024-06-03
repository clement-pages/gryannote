import gradio as gr

from gryannote.audio import AnnotatedAudio
from gryannote.pipeline import PipelineSelector
from gryannote.rttm import RTTMHandler

from pyannote.audio import Pipeline

example = AnnotatedAudio().example_inputs()

annotated_audio = AnnotatedAudio(type="filepath", interactive=True)


def apply_pipeline(pipeline: Pipeline, audio):
    """Apply specified pipeline on the indicated audio file"""
    annotations = pipeline(audio)

    return ((audio, annotations), (audio, annotations))


def update_annotations(data):
    return rttm_handler.on_edit(data)


with gr.Blocks() as demo:
    gr.Markdown(
        "Welcome to the [pyannote.audio](https://github.com/pyannote/pyannote-audio) app !"
    )

    #login_button = gr.LoginButton()

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
        interactive=True,
    )

    run_btn = gr.Button("Run pipeline")

    rttm_handler = RTTMHandler()

    annotated_audio.edit(
        fn=update_annotations,
        inputs=annotated_audio,
        outputs=rttm_handler,
        preprocess=False,
        postprocess=False,
    )

    run_btn.click(
        fn=apply_pipeline,
        inputs=[pipeline_selector, annotated_audio],
        outputs=[annotated_audio, rttm_handler],
    )


if __name__ == "__main__":
    demo.launch()
