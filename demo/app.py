import threading

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

PHASE_MESSAGES = [
    "세그멘테이션 처리 중...",
    "음성 임베딩 추출 중...",
    "클러스터링 분석 중...",
    "화자 분리 마무리 중...",
]


def apply_pipeline(pipeline, audio, progress=gr.Progress()):
    """Apply specified pipeline on the indicated audio file"""
    if not audio or not isinstance(audio, str):
        raise gr.Error("Please upload an audio file first")

    progress(0.05, desc="하이퍼파라미터 적용 중...")
    pipeline.instantiate(OPTIMAL_PARAMS)

    result_holder = [None]
    error_holder = [None]

    def run_inference():
        try:
            result_holder[0] = pipeline(audio)
        except Exception as e:
            error_holder[0] = e

    thread = threading.Thread(target=run_inference)
    thread.start()

    tick = 0
    progress(0.1, desc="화자 분리 파이프라인 실행 중...")
    while thread.is_alive():
        thread.join(timeout=2.0)
        if thread.is_alive():
            tick += 1
            frac = min(0.10 + tick * 0.05, 0.85)
            msg = PHASE_MESSAGES[min(tick // 3, len(PHASE_MESSAGES) - 1)]
            progress(frac, desc=msg)

    if error_holder[0]:
        raise gr.Error(
            f"An error occurred while processing audio: {error_holder[0]}"
        )

    output = result_holder[0]

    progress(0.9, desc="결과 처리 중...")

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

    run_btn = gr.Button("Run pipeline & Create labels")

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
