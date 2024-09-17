import gradio as gr
from gryannote_audio import AudioLabeling, Player
from pyannote.audio import Pipeline
from pyannote.database.util import load_rttm

audio = "/home/clement-pages/gryannote/sample.wav"
annotations = load_rttm("/home/clement-pages/gryannote/sample.rttm")["sample"]

player = AudioLabeling(audio=audio, annotations=annotations, show_spectrogram=False)

demo = gr.Interface(lambda x: x, inputs=None, outputs=player)


if __name__ == "__main__":
    demo.launch()
