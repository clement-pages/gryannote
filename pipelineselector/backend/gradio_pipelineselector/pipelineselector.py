from __future__ import annotations

import warnings
from typing import Any, Callable, Literal, List

from pyannote.audio import Pipeline
from gradio.components.base import FormComponent
from gradio.events import Events

from huggingface_hub import HfApi


class PipelineSelector(FormComponent):
    """
    Creates a dropdown of choices from which a single entry or multiple entries can be selected (as an input component) or displayed (as an output component).

    Demos: sentence_builder, titanic_survival
    """

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
        choices: list[str | int | float | tuple[str, str | int | float]] | None = None,
        pipeline: Pipeline | None = None,
        *,
        value: str | int | float | list[str | int | float] | Callable | None = None,
        source: Literal["dropdown", "instance"] = "dropdown",
        token: str | None = None,
        allow_custom_value: bool = False,   #TODO remove this argument
        filterable: bool = True,
        label: str | None = None,
        info: str | None = None,
        every: float | None = None,
        show_label: bool | None = None,
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
        Parameters:
            choices: A list of string options to choose from. An option can also be a tuple of the form (name, value), where name is the displayed name of the dropdown choice and value is the value to be passed to the function, or returned by the function.
            A value for this argument must be provided if `source` argument is set to `dropdown` (default value)
            value: default value(s) selected in dropdown. If None, no value is selected by default. If callable, the function will be called whenever the app loads to set the initial value of the component.
            pipeline: An instance of a pipeline to use. A value for this argument must be provied if `source` is set to `pipeline`.
            type: Type of value to be returned by component. "value" returns the string of the choice selected, "index" returns the index of the choice selected.
            multiselect: if True, multiple choices can be selected.
            allow_custom_value: If True, allows user to enter a custom value that is not in the list of choices.
            max_choices: maximum number of choices that can be selected. If None, no limit is enforced.
            filterable: If True, user will be able to type into the dropdown and filter the choices by typing. Can only be set to False if `allow_custom_value` is False.
            label: The label for this component. Appears above the component and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component is assigned to.
            info: additional component description.
            every: If `value` is a callable, run the function 'every' number of seconds while the client connection is open. Has no effect otherwise. The event can be accessed (e.g. to cancel it) via this component's .load_event attribute.
            show_label: if True, will display label.
            container: If True, will place the component in a container - providing some extra padding around the border.
            scale: relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.
            min_width: minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.
            interactive: if True, choices in this dropdown will be selectable; if False, selection will be disabled. If not provided, this is inferred based on whether the component is used as an input or output.
            visible: If False, component will be hidden.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, component will not be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
        """

        valid_source = ["dropdown", "instance"]
        if source not in valid_source:
            raise ValueError(f"Value for `source` is not valid: {source}. Valid values are {valid_source}")

        if source == "dropdown":
            if not choices:
                self.choices = self.get_available_pipelines()
            else:
                self.choices = choices
        else:
            if not pipeline:
                raise ValueError(
                    "Incorrect usage: A pipeline must be specified using `pipeline` argument, as value for source argument has been set to instance"
                )
            if not pipeline or not isinstance(pipeline, Pipeline):
                raise ValueError(f"Incorrect value or type for `pipeline`: {pipeline}")
            if visible:
                visible = False
                warnings.warn("Component cannot be visible when source set to instance")
            self.pipeline = pipeline

        self.source = source
        self.token = token

        if not filterable and allow_custom_value:
            filterable = True
            warnings.warn(
                "The `filterable` parameter cannot be set to False when `allow_custom_value` is True. Setting `filterable` to True."
            )

        self.allow_custom_value = allow_custom_value
        self.filterable = filterable
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

    def api_info(self) -> dict[str, Any]:
        if self.source == "dropdown":
            json_type = {
                "type": "string",
                "enum": [c[1] for c in self.choices],
            }
        else:
            json_type = {
                "type": {},
            }
        return json_type

    def example_inputs(self) -> Any:
        if self.source == "dropdown":
            return self.choices[0][1]
        return None

    def preprocess(self, payload: str | None) -> Pipeline:
        """
        Parameters:
            payload: the value of the selected dropdown choice if source has been set to `dropdown`
            or None if source has been set to `instance`
        Returns:
            An instanciated pipeline
        """
        print(payload)
        if self.source == "dropdown":
            self.pipeline = Pipeline.from_pretrained(payload, use_auth_token=self.token)
        else:
            if payload:
                warnings.warn("Payload is not empty, whereas source has been set to `instance`")
        return self.pipeline

    def postprocess(
        self, value: Pipeline | None
    ) -> str | None:
        """
        Parameters:
            value: instanciated pipeline
        Returns:
            Returns the values of the selected dropdown entry or entries.
        """
        if not value:
            return None
        else:
            return value.__repr__

    def get_available_pipelines(self) -> List[str]:
        """Get official pyannote pipelines from Hugging Face
        
        Returns
        -------
            list of default available pyannote pipelines
        """
        available_pipelines = [
            p.modelId for p in HfApi().list_models(filter="pyannote-audio-pipeline", sort="last_modified", direction=-1)
        ]
        return list(filter(lambda p: p.startswith("pyannote/"), available_pipelines))
