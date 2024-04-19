# ANNOTATED AUDIO GRADIO COMPONENT

This repository regroups `pyannote` custom `gradio` components.

## Installation

To install components (still in devlopment) contained in this reposetory, follow these instructions.

0 - Create a virtual environment (for example using `micromamba`) and activate it
```shell
micromamba create -n pyannote-gradio
micromamba activate pyannote-gradio
```

1 - Install python 3.8+:
```shell
micromamba install python=3.10 -c conda-forge
```

2 - Install `pyannote-audio` and `gradio`:
```shell
pip install -U pyannote.audio gradio
```

3 - Install npm 9+ and node.js v16.14+
```shell
nvm install node
npm install -g npm
```

4 - Clone this repository in your favorite directory
```shell
git clone git@github.com:clement-pages/pyannote-gradio.git
cd pyannote-gradio/annotatedaudio
```

Then, you can use the component in development mode:
```shell
gradio cc install
gradio cc dev
```


## Keyboard shortcuts

The following table summarizes available keyboard shortcuts for the `AnnotatedAudio` component:

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
|`BACKSAPCE`                                    | Delete selected annotation and select the previous one                |
|`DELETE` or `SHIFT + BACKSPACE`                | Delete selected region and select the next one                        |
|`ESC`                                          | Unselect selected annotation and / or label                           |
| `UP` or `DOWN`                                | Zoom in/out                                                           |
