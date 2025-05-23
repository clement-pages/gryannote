# Changelog

## main

### New features

- add a timeline on the audio player. Timeline's style can be customised using the new `timeline_options` attribute of `AudioLabeling` component.
See `TimelineOptions` documentation for more details about available options
- add timestamp when hovering over waveform with mouse cursor. This feature can be custom using th nex `hover_options` attribute of `AudioLabeling` component.
See `HoverOptions` documentation for more details about available options
- add support for video:
```python
from gryannote_audio import Player
player = Player(video="video.mp4")
```
A video file can also be upload directly from the interface when using `AudioLabeling` in interactive mode.
- beep on annotation in/out, to check alignment between audio and annotation. This feature can be enabled directly
from `AudioLabeling`'s interface.

### Fixes

- fix(audio): fix playback of a previously loaded audio when loading and playing a new one
- fix(audio): do not allow to edit regions and caption when using static mode of `gryannote_audio`

### improvements

- minimap's waveform is now colored according to segments added on the player.
- improve behavior of region's button (remove and trim button). Now these buttons will keep focus while the user is in removing or trimming mode, respectively. Also, it is now possible to remove or trim several regions in a row, without having to click
again on the corresponding button.
- add a region by dragging on an empty space of the waveform, instead of double clicking. This allows to set a region with custom end bound.

## 0.3.0

### Breaking changes

- RTTM postprocessing no longer needs the audio to be passed as return value of the wrapped function, only `pyannote.core.Annotation`. (see `app/demo.py`)

### backend API

- add new component: `gryannote_audio.Player`. This component is dedicated to visualization purposes:
```python
audio = ...
annotations = ...

# Equivalent to player = AudioLabeling(audio=audio, annotations=annotations, interactive=False, type="filepath")
player = Player(audio=audio, annotations=annotations)

demo = gr.Interface(lambda x : x, inputs=None, outputs=player)
```

- add `default_pipeline` parameter to `PipelineSelection`. This parameter allows to select a default pipeline for the component's pipeline dropdown.
```python
    pipeline_selector = PipelineSelector(default_pipeline="pyannote/speaker-diarization-3.1")
```

- The RTTM component can now be used to upload annotations to the audio labeling one!
```python
audio_labeling = AudioLabeling(type="filepath")

rttm = RTTM()
rttm.upload(
    fn=audio_labeling.load_annotations,
    inputs=[audio_labeling, rttm],
    outputs=audio_labeling,
)
```

### improvements

- **label an audio using a gamepad!** See [here](https://github.com/clement-pages/gryannote/tree/audio-labeling-with-gamepad/gryannote/audio#gamepad-shortcuts) to check the available shortcuts.
⚠️ This feature has been tested with a Battletron Nintendo Switch on Firefox, and may not work with any other device or browser.
- add a minimap of the waveform on audio component. This minimap can be enable / disable by setting `show_minimap` to `True` (default) / `False` when instantiating `AudioLabeling`. For now, only the waveform
is displayed on the minimap, but it is planned to also show annotation in a future release.
- if audio is playing, time cursor will not jump to the start of the active annotation
- if audio is paused, time cursor will be set to the start of the active annotation only if this annotation is not visible on the screen.
- replace arithmetic zoom (z = z + delta) by a geometric one (z = z * coef)
- add new shortcuts to speed up zoom in / zoom out: `SHIFT+UP` / `SHIFT+DOWN`
- Management of overlapped regions is now devolved to `@gryannote/wavesurfer.js`

### fixes

- fix display of overlapping regions when splitting an annotation
- fix text not visible in the label name setting box when using dark mode

## 0.2.0

### backend API
- add two new parameters to `AudioLabeling` constructor: `audio` and `annotations`. These two parameters can be used to init an `AudioLabeling` component with specified audio and annotations, for visualization purposes for instance.
```python
audio = ...       # str, Path or (int, numpy.ndarray)
annotations = ... # pyannote.core.Annotation
audio_labeling = AudioLabeling(type="filepath", interactive=True, audio=audio, annotations=annotations)
```

### improvements
- move time cursor so that active segment is always visible on the screen
- improve `AudioLabeling` zoom interface
- add more error messages on the UI

### dependency
- remove dependency to `networkx`
