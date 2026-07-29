import gradio as gr
from gryannote_audio import AudioLabeling
from gryannote_pipeline import PipelineSelector
from gryannote_rttm import RTTM


OPTIMAL_PARAMS = {
    "segmentation": {"min_duration_off": 0.0},
    "clustering": {
        "method": "centroid",
        "min_cluster_size": 12,
        "threshold": 0.7045654963945799,
    },
}


def apply_pipeline(pipeline, audio):
    """Apply specified pipeline on the indicated audio file"""
    if not audio or not isinstance(audio, str):
        raise gr.Error("Please upload an audio file first")

    pipeline.instantiate(OPTIMAL_PARAMS)

    try:
        output = pipeline(audio)
    except (ValueError, RuntimeError) as e:
        raise gr.Error(f"An error occurred while processing audio: {e}")

    # pyannote 3.x returns DiarizeOutput; extract the Annotation
    if hasattr(output, "speaker_diarization"):
        annotations = output.speaker_diarization
    else:
        annotations = output

    return ((audio, annotations), annotations)


with gr.Blocks() as demo:
    gr.Markdown(
        "[Gryannote](): The [pyannote](https://github.com/pyannote/pyannote-audio) audio labeling tool"
    )

    pipeline_selector = PipelineSelector(
        default_pipeline="pyannote/speaker-diarization-3.1"
    )
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
    rttm.upload(
        fn=audio_labeling.load_annotations,
        inputs=[audio_labeling, rttm],
        outputs=audio_labeling,
    )

    audio_labeling.edit(
        fn=rttm.on_edit,
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
