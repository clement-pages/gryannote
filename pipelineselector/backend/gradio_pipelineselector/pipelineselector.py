from __future__ import annotations

import warnings
from typing import Any, Callable, Dict, List, Optional, Tuple

from gradio.components.base import FormComponent
from gradio.data_classes import GradioModel
from gradio.events import Events
from huggingface_hub import HfApi
from pyannote.audio import Pipeline
from pyannote.pipeline.parameter import (
    Categorical,
    DiscreteUniform,
    Frozen,
    Integer,
    LogUniform,
    ParamDict,
    Uniform,
)


class PipelineInfo(GradioModel):
    # name of the pipeline:
    name: str
    # token used to load the pipeline, if needed:
    token: Optional[str]
    # pipeline's parameters specifications
    param_specs: Optional[Dict]


class PipelineSelector(FormComponent):
    """
    Enable the user to select a pipeline and edit its hyperparameters
    """

    data_model = PipelineInfo

    EVENTS = [
        Events.change,
        Events.input,
        Events.select,
        Events.focus,
        Events.blur,
        Events.key_up,
    ]

    def __init__(
        self,
        pipelines: Optional[
            Pipeline | List[str] | Dict[str, Pipeline] | Tuple[str, Pipeline]
        ] = None,
        *,
        value: str | Callable | None = None,
        token: str | None = None,
        label: str | None = None,
        info: str | None = None,
        every: float | None = None,
        show_label: bool = True,
        show_config: bool = False,
        enable_edition: bool = False,
        container: bool = True,
        scale: int | None = None,
        min_width: int = 160,
        interactive: bool | None = None,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
    ):
        """
        Parameters
        ----------
        pipelines: optional
            Can be a:
                - instantiated pyannote pipeline
                - list of possible pipeline name. This list must be subset of pyannote pipelines
                   available on Hugging Face
                - list of (pipeline name, pipeline instance)
                - dict {pipeline name : pipeline instance}
            By default, the component ask the user to select a pipeline from a dropdown with
            available pyannote pipeline on Hugging Face
        value: optional
            default value selected in dropdown. If None, no value is selected by default.
            If callable, the function will be called whenever the app loads to set the initial value
            of the component.
        label: optional
            The label for this component. Appears above the component and is also used as the header
            if there are a table of examples for this component. If None and used in a `gr.Interface`,
            the label will be the name of the parameter this component is assigned to.
        info: optional
            additional component description.
        every: optional
            If `value` is a callable, run the function 'every' number of seconds while the client
            connection is open. Has no effect otherwise. The event can be accessed (e.g. to cancel it)
            via this component's .load_event attribute.
        show_label: optional
            If True, will display label.
        show_config: bool, optional
            If True, will display pipeline hyperparameters configuration interface as soon as a pipeline
            has been loaded. Has no effect if `enable_edition` is set to False. Default to False.
        enable_edition: bool, optional
            If True, let the user to update pipeline's hyperparameters
        container: optional
            If True, will place the component in a container - providing some extra padding around
            the border.
        scale: optional
            relative size compared to adjacent Components. For example if Components A and B are in
            a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an
            integer. scale applies in Rows, and to top-level Components in Blocks where
            fill_height=True.
        min_width: optional
            minimum pixel width, will wrap if not sufficient screen space to satisfy this value.
            If a certain scale value results in this Component being narrower than min_width,
            the min_width parameter will be respected first.
        interactive: optional
            if True, choices in this dropdown will be selectable; if False, selection will be disabled.
            If not provided, this is inferred based on whether the component is used as an input or output.
        visible: optional
            If False, component will be hidden. Default to True.
        elem_id: optional
            An optional string that is assigned as the id of this component in the HTML DOM.
            Can be used for targeting CSS styles.
        elem_classes: optional
            An optional list of strings that are assigned as the classes of this component in the HTML DOM.
            Can be used for targeting CSS styles.
        render: optional
            If False, component will not be rendered in the Blocks context.
            Should be used if the intention is to assign event listeners now but render the component later.
        """

        self._pipeline_map: Dict[str, Pipeline] = None

        if not pipelines:
            self.pipelines = [(p, p) for p in self.get_available_pipelines()]

        elif isinstance(pipelines, Pipeline):
            self._pipeline = pipelines

        elif isinstance(pipelines, list) and isinstance(pipelines[0], str):
            available_pipelines = self.get_available_pipelines()
            self.pipelines = []
            for pipeline in pipelines:
                if pipeline not in available_pipelines:
                    warnings.warn(f"Pipeline {pipeline} is not available. Skipping it.")
                    continue
                self.pipelines.append((pipeline, pipeline))

        elif isinstance(pipelines, list) and isinstance(pipelines[0], tuple):
            self._pipeline_map = dict(pipelines)
            self.pipelines = [(name, name) for name, _ in pipelines]

        elif isinstance(pipelines, dict):
            self._pipeline_map = dict(pipelines.items())
            self.pipelines = [(name, name) for name in pipelines]

        else:
            raise ValueError(
                "pipeline must be an instantiated pipeline, a list of pipeline name,",
                "a list of (pipeline name, pipeline instance) or a dict of pipeline name",
                "pipeline instance",
            )

        self.token = token

        # component is visible only if a pipeline was not already set
        visible = getattr(self, "_pipeline", None) is None


        self.show_config = show_config
        self.enable_edition = enable_edition

        super().__init__(
            label=label,
            info=info,
            every=every,
            show_label=show_label,
            container=container,
            scale=scale,
            min_width=min_width,
            interactive=interactive,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            value=value,
        )

    def example_inputs(self) -> Any:
        """Return example inputs"""
        if getattr(self, "pipelines", None):
            return self.pipelines[0][1]

        return getattr(self, "_pipeline", None)

    def preprocess(self, payload: PipelineInfo | None) -> Pipeline:
        """
        Parameters:
            payload: PipelineInfo
                info about the pipeline selected by the user in the frontend,
                None if pipeline was directly set in the backend
        Returns:
            An instantiated pipeline
        """
        if not getattr(self, "_pipeline", None):
            if not payload:
                raise ValueError(
                    "Cannot instantiate a pipeline as no pipeline",
                    "was provided in the backend or in the interface",
                )
            self._pipeline = self._load_pipeline(payload)
        return self._pipeline

    def postprocess(self, value: Pipeline | None) -> str | None:
        """
        Parameters:
            value: instantiated pipeline
        Returns:
            Returns the values of the selected dropdown entry or entries.
        """
        if not value:
            return None
        return value.__repr__

    def on_select(self, value: Dict):
        """Update pipeline according to selected value from frontend"""
        pipeline_info = PipelineInfo(**value)
        self._pipeline = self._load_pipeline(pipeline_info)
        param_types = self._pipeline.parameters(instantiated=False)
        param_values = self._pipeline.parameters(instantiated=True)
        pipeline_info.param_specs = self._get_param_specs(param_types, param_values)

        return pipeline_info

    def on_change(self, value: Dict):
        """Update selected pipeline's parameters"""
        pipeline_info = PipelineInfo(**value)
        param_types = self._pipeline.parameters(instantiated=False)
        param_values = self._get_param_values(param_types, pipeline_info.param_specs)
        self._pipeline = self._pipeline.instantiate(param_values)
        return pipeline_info

    def get_available_pipelines(self) -> List[str]:
        """Get official pyannote pipelines from Hugging Face

        Returns
        -------
            list of default available pyannote pipelines
        """
        available_pipelines = [
            p.modelId
            for p in HfApi().list_models(
                filter="pyannote-audio-pipeline", sort="last_modified", direction=-1
            )
        ]
        return list(filter(lambda p: p.startswith("pyannote/"), available_pipelines))

    def _get_param_values(
        self, param_types: Dict[str, Any], param_specs: Dict[str, Any]
    ) -> Dict[str, Any]:
        param_values = {}
        for param, specs in param_specs.items():
            param_type = param_types[param]
            if isinstance(param_type, (ParamDict, Dict)):
                param_values[param] = self._get_param_values(param_type, specs)
            else:
                if isinstance(param_type, (DiscreteUniform, Integer)):
                    param_values[param] = int(specs["value"])
                elif isinstance(param_type, (Uniform, LogUniform)):
                    param_values[param] = float(specs["value"])
                else:
                    param_values[param] = specs["value"]
        return param_values

    def _load_pipeline(self, pipeline_info: PipelineInfo) -> Pipeline:

        if pipeline_info.token != "":
            self.token = pipeline_info.token
        if self._pipeline_map:
            pipeline = self._pipeline_map[pipeline_info.name]
        else:
            pipeline = Pipeline.from_pretrained(
                pipeline_info.name, use_auth_token=self.token
            )
        return pipeline

    def _get_param_specs(self, param_types: Dict, param_values: Dict) -> Dict:
        param_specs = {}

        for param_name, param in param_types.items():
            param_specs[param_name] = {}
            if isinstance(param, (ParamDict, Dict)):
                param_specs[param_name] = self._get_param_specs(
                    param, param_values[param_name]
                )

            elif isinstance(param, Categorical):
                param_specs[param_name]["component"] = "dropdown"
                param_specs[param_name]["choices"] = param.choices
                param_specs[param_name]["value"] = param_values[param_name]

            elif isinstance(param, (DiscreteUniform, Uniform, LogUniform, Integer)):
                param_specs[param_name]["component"] = "slider"
                param_specs[param_name]["value"] = str(param_values[param_name])
                param_specs[param_name]["min"] = str(param.low)
                param_specs[param_name]["max"] = str(param.high)
                if isinstance(param, DiscreteUniform):
                    param_specs[param_name]["step"] = str(param.q)
                elif isinstance(param, Integer):
                    param_specs[param_name]["step"] = "1"
                else:
                    param_specs[param_name]["step"] = "any"

            elif isinstance(param, Frozen):
                # just for printing purpose
                param_specs[param_name]["component"] = "textbox"
                param_specs[param_name]["value"] = str(param_values[param_name])

            else:
                raise TypeError(f"Unknown type for {param_name} (type = {type(param)})")

        return param_specs
