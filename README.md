<p align="center">
  <img src="https://github.com/clement-pages/gryannote/blob/main/docs/assets/logo-gryannote.png?raw=true" alt="gryannote logo" width="200">
<p>

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

The following code snippet show how to use the `gryannote_audio` component with a `pyannote` pipeline in just a few lines of code. You can find a complete example that uses the three component
in `app.py` script.

```python
import gradio as gr
from gryannote_audio import AudioLabeling
from pyannote.audio import Pipeline

audio_labeling = AudioLabeling(type="filepath", interactive=True)


def apply_pipeline(audio):
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1")
    annotations = pipeline(audio)
    return (audio, annotations)

demo = gr.Interface(apply_pipeline, inputs=audio_labeling, outputs=audio_labeling)

demo.launch()
```

## Interface

Launching `demo/app.py` script will generate the following interface. This interface uses the three `gryannote` components. More details about these components and their interface can be found
in their respective README.

![](https://github.com/clement-pages/gryannote/blob/main/docs/assets/gryannote_interface.png?raw=1)

RTTM annotations in RTTM component are dynamically updated according to the audio labeling made in the audio component.

## Try it!

A `gryannote` app can be runned in this [Hugging Face space](https://huggingface.co/spaces/clement-pages/gryannote)

## Citation

If you are using `gryannote`, please use the following citation:

```bibtex
@inproceedings{pages24_interspeech,
  title     = {Gryannote open-source speaker diarization labeling tool},
  author    = {Clément Pages and Hervé Bredin},
  year      = {2024},
  booktitle = {Interspeech 2024},
  pages     = {3650--3651},
}
```
