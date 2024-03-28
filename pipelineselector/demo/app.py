
import gradio as gr
from gradio_pipelineselector import PipelineSelector
from pyannote.audio import Pipeline
import os


example = PipelineSelector().example_inputs()

pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=os.environ["HG_TOKEN"])

demo = gr.Interface(
    lambda x:x,
    inputs=PipelineSelector(), 
    outputs=PipelineSelector(pipelines=pipeline),
    # examples=[[example]],  # uncomment this line to view the "example version" of your component
)


if __name__ == "__main__":
    demo.launch()
