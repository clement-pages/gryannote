import gradio as gr
from gryannote_audio import AudioLabeling
from gryannote_pipeline import PipelineSelector
from gryannote_rttm import RTTM
from pyannote.audio import Pipeline


def apply_pipeline(pipeline: Pipeline, audio):
    """Apply specified pipeline on the indicated audio file"""
    try:
        annotations = pipeline(audio)
    except (ValueError, RuntimeError) as e:
        raise gr.Error(f"An error occurred while processing audio: {e}")

    return ((audio, annotations), (audio, annotations))


def update_annotations(data):
    return rttm.on_edit(data)


with gr.Blocks() as demo:
    gr.Markdown(
        "[Gryannote](): The [pyannote](https://github.com/pyannote/pyannote-audio) audio labeling tool"
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
    audio_labeling = AudioLabeling(
        type="filepath",
        interactive=True,
    )

    run_btn = gr.Button("Run pipeline")

    rttm = RTTM()

    audio_labeling.edit(
        fn=update_annotations,
        inputs=audio_labeling,
        outputs=rttm,
        preprocess=False,
        postprocess=False,
    )

    run_btn.click(
        fn=apply_pipeline,
        inputs=[pipeline_selector, audio_labeling],
        outputs=[audio_labeling, rttm],
    )


if __name__ == "__main__":
    demo.launch()
