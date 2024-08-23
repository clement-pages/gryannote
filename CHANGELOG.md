# Changelog

## develop

### improvement

- if audio is playing, time cursor will not jump to the start of the active annotation
- if audio is paused, time cursor will be set to the start of the active annotation only if this annotation is not visible on the screen.

## 0.2.0

### backend API
- add two new parameters to `AudioLabeling` constructor: `audio` and `annotations`. These two parameters can be used to init an `AudioLabeling` component with specified audio and annotations, for visualization purposes for instance.
```python
audio = ...       # str, Path or (int, numpy.ndarray)
annotations = ... # pyannote.core.Annotation
audio_labeling = AudioLabeling(type="filepath", interactive=True, audio=audio, annotations=annotations)
```

### improvement
- move time cursor so that active segment is always visible on the screen
- improve `AudioLabeling` zoom interface
- add more error messages on the UI

### dependency
- remove dependency to `networkx`
