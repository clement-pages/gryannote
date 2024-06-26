import gradio as gr
from gryannote_audio import AudioLabeling
from gryannote_rttm import RTTM


def update_annotations(data):
    return rttm.on_edit(data)


with gr.Blocks() as demo:
    audio_labeling = AudioLabeling(
        type="filepath",
        interactive=True,
    )

    rttm = RTTM()

    audio_labeling.edit(
        fn=update_annotations,
        inputs=audio_labeling,
        outputs=rttm,
        preprocess=False,
        postprocess=False,
    )


if __name__ == "__main__":
    demo.launch()
