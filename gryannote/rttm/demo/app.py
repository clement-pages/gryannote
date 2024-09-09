import gradio as gr
from gryannote_audio import AudioLabeling
from gryannote_rttm import RTTM

with gr.Blocks() as demo:
    audio_labeling = AudioLabeling(
        type="filepath",
        interactive=True,
    )

    rttm = RTTM()

    audio_labeling.edit(
        fn=rttm.on_edit,
        inputs=audio_labeling,
        outputs=rttm,
        preprocess=False,
        postprocess=False,
    )

    rttm.upload(
        fn=audio_labeling.load_annotations,
        inputs=[audio_labeling, rttm],
        outputs=audio_labeling,
    )


if __name__ == "__main__":
    demo.launch()
