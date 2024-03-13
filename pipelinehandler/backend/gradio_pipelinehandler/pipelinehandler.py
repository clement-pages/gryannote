from typing import Any, Callable, Optional, Text

from gradio.components.base import Component
from gradio.data_classes import FileData, GradioModel
from gradio.events import Events

from huggingface_hub import HfApi

from pyannote.audio import Pipeline


class PipelineConfig(GradioModel):
    config: FileData | Text
    auth_token: Optional[Text]


class PipelineHandler(Component):

    data_model = PipelineConfig

    EVENTS = [
        Events.select,
    ]

    def __init__(
            self,
            value: Any = None,
            *, 
            label: str | None = None, 
            info: str | None = None,
            show_label: bool | None = None, 
            container: bool = True, 
            scale: int | None = None, 
            min_width: int | None = None, 
            interactive: bool | None = None,
            visible: bool = True,
            elem_id: str | None = None, 
            elem_classes: list[str] | str | None = None, 
            render: bool = True, 
            load_fn: Callable[..., Any] | None = None, 
            every: float | None = None
        ):
        super().__init__(
            value, 
            label=label, 
            info=info, 
            show_label=show_label, 
            container=container, scale=scale, 
            min_width=min_width,
            interactive=interactive, 
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            load_fn=load_fn,
            every=every
        )

    def preprocess(self, payload: PipelineConfig | None):
        """
        Load a pipeline

        Parameters
        ----------
        payload : tuple
            payload contains path to pipeline config file or Hugging Face pipeline name,
            and authentification token to access corresponding pipeline, if needed
        
        Returns
        -------
        pipeline:
            a ready-to-use pyannote pipeline
        """
        if payload is None:
            return None
        
        if isinstance(payload.config, FileData):
            payload = payload.path
        pipeline = Pipeline.from_pretrained(
            payload.config,
            use_auth_token=payload.auth_token,
        )

        return pipeline


    def postprocess(self, value):

        return value

    def example_inputs(self):
        return {"foo": "bar"}

    def api_info(self):
        return {"type": {}, "description": "any valid json"}
    
    def get_pipeline_params(pipeline_name: str):
        """Get pipeline's list of parameters, with their default value"""
        print(pipeline_name)
