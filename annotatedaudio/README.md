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
pip install pyannote.audio gradio
```

3 - Install npm 9+ and node.js v16.14+
```shell
npm install -g npm
nvm install node
```

4 - Clone this repository in your favorite directory
```shell
git clone git@github.com:clement-pages/pyannote-gradio.git
cd pyannote-gradio/annotatedaudio
```

5 - Install the component
```shell
gradio cc install
```

6 - Launch component's demo in a local server:
```shell
gradio cc dev
```