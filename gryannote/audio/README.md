# GRYANNOTE-AUDIO: AUDIO LABELING GRADIO COMPONENT

The gryannote audio component provides an interface to annotate an audio. It is powered by [wavesurfer.js](https://wavesurfer.xyz/).

## Installation

```shell
pip install gryannote-audio
```

## Component usage example

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

Here's the audio component interface when the interface is accessed

![](https://github.com/clement-pages/gryannote/blob/main/docs/assets/gryannote_audio_upload_interface.png?raw=1)

The component offers two ways of loading audio: either by loading a file, or by directly recording a conversation using the interface. After loading an audio, the component will display the following interface:

![](https://github.com/clement-pages/gryannote/blob/main/docs/assets/gryannote_audio_with_loaded_audio.png?raw=1)

Then, it is possible to add annotations on the audio waveform by double clicking on it, or by using shortcut. All available shortcuts are enumareted in the following table.

![](https://github.com/clement-pages/gryannote/blob/main/docs/assets/gryannote_audio_with_annotations.png?raw=1)



## Keyboard shortcuts

The following table summarizes available keyboard shortcuts for the `AudioLabeling` component:

| Shortcut                                      | Action                                                                |
| --------------------------------------------- | --------------------------------------------------------------------- |
| `SPACE`                                       | Toggle play / pause                                                   |
| `ENTER`                                       | Create annotation at current time                                     |
| `SHIFT + ENTER`                               | Split annotation at current time                                      |
| `A`, `B`, `C`, ..., `Z`                       | Set active label. If there is a selected annotation, update its label |
| `LEFT` or `RIGHT`                             | Edit start time of selected annotation (if any) or move time cursor   |
| `SHIFT + LEFT` or `SHIFT + RIGHT`             | Same, but faster                                                      |
|`ALT + LEFT` or `ALT + RIGHT`                  | Edit end time of selected annotation                                  |
| `SHIFT + ALT + LEFT` or `SHIFT + ALT + RIGHT` | Same, but faster                                                      |
| `TAB`                                         | Select next annotation                                                |
| `SHIFT + TAB`                                 | Select previous annotation                                            |
|`BACKSPACE`                                    | Delete selected annotation and select the previous one                |
|`DELETE` or `SHIFT + BACKSPACE`                | Delete selected region and select the next one                        |
|`ESC`                                          | Unselect selected annotation and / or label                           |
| `UP` or `DOWN`                                | Zoom in/out                                                           |
| `SHIFT + UP` or `SHIFT + DOWN`                | Same, but faster                                                      |
| `F2`                                          | Open settings for the active label                                    |
