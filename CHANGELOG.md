# Changelog

## main

### Breaking changes

- RTTM postprocessing does not need anymore the audio to be passed as return value of wrapped function, only `pyannote.core.Annotation`.

### backend API

- add new component: `gryannote_audio.Player`. This component is dedicated to visualization purposes:
```python
audio = ...
annotations = ...

# Equivalent to player = AudioLabeling(audio=audio, annotations=annotations, interactive=False, type="filepath")
player = Player(audio=audio, annotations=annotations)

demo = gr.Interface(lambda x : x, inputs=None, outputs=player)
```

- add `default_pipeline` parameter to `PipelineSelection`. This parameter allows to select a default pipeline for the component dropdown.
```python
    pipeline_selector = PipelineSelector(default_pipeline="pyannote/speaker-diarization-3.1")
```

- The RTTM component can now be used to upload annotations to the audio labeling one !
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
- Managing of region overlapped is now devolved to `@gryannote/wavesurfer.js`

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
