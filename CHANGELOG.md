# Changelog

## main

### backend API

- add new component: `gryannote_audio.Player`. This component is dedicated to visualization purposes:
```python
audio = ...
annotations = ...

# Equivalent to player = AudioLabeling(audio=audio, annotations=annotations, interactive=False, type="filepath")
player = Player(audio=audio, annotations=annotations)

demo = gr.Interface(lambda x : x, inputs=None, outputs=player)
```

### improvements
- replace arithmetic zoom (z = z + delta) by a geometric one (z = z * coef)
- add new shortcuts to speed up zoom in / zoom out: `SHIFT+UP` / `SHIFT+DOWN`

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
