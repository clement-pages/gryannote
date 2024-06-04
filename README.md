# gryannote: a  speaker diarization labeling tool

gryannote is a collection of [`Gradio`](https://www.gradio.app/) custom components focusing on the labeling of speaker diarization data. Integrated with the [`pyannote`](https://github.com/pyannote/pyannote-audio) speaker diarization ecosystem, it allows to build web applications to load pretrained `pyannote` pipelines and customize their hyper-parameters, upload or record an audio file, process it with the pipeline, visualize and interact with its outputs, correct them if needed, and export the final annotation in RTTM format. Each of these components can be used independently from each other.

## Available `Gradio` custom components

Here is the list of `Gradio` custom components integrated in `gryannote`

- [gryannote_audio](https://github.com/clement-pages/gryannote/tree/main/gryannote/audio/README.md)
- [gryannote_pipeline](https://github.com/clement-pages/gryannote/tree/main/gryannote/pipeline/README.md)
- [gryannote_rttm](https://github.com/clement-pages/gryannote/tree/main/gryannote/rttm/README.md)

## Installation

```shell
pip install gryannote
```

## Usage

The following code snippet show how to use the `gryannote_audio` component with a `pyannote` pipeline in just a few lines of code
```python
import gradio as gr
from gryannote.audio import AnnotatedAudio
from pyannote.audio import Pipeline

annotated_audio = AnnotatedAudio(type="filepath", interactive=True)


def apply_pipeline(audio):
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1")
    annotations = pipeline(audio)
    return (audio, annotations)

demo = gr.Interface(apply_pipeline, inputs=annotated_audio, outputs=annotated_audio)

demo.launch()
```

## Try it !

A version of the `gryannote` app is available in this [Hugging Face space](https://huggingface.co/spaces/clement-pages/gryannote)

## Citation

TODO