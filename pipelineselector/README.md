
# `gradio_pipelineselector`
<img alt="Static Badge" src="https://img.shields.io/badge/version%20-%200.0.2%20-%20orange">  

A component allowing a user to select a pipeline from a drop-down list

## Installation

```bash
pip install gradio_pipelineselector
```

## Usage

```python

import gradio as gr
from gradio_pipelineselector import PipelineSelector
from pyannote.audio import Pipeline
import os


example = PipelineSelector().example_inputs()

pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=os.environ["HG_TOKEN"])

demo = gr.Interface(
    lambda x:x,
    PipelineSelector(source="dropdown"), 
    PipelineSelector(source="instance", pipeline=pipeline)
    # examples=[[example]],  # uncomment this line to view the "example version" of your component
)


if __name__ == "__main__":
    demo.launch()

```

## `PipelineSelector`

### Initialization

<table>
<thead>
<tr>
<th align="left">name</th>
<th align="left" style="width: 25%;">type</th>
<th align="left">default</th>
<th align="left">description</th>
</tr>
</thead>
<tbody>
<tr>
<td align="left"><code>choices</code></td>
<td align="left" style="width: 25%;">

```python
list[str | int | float | tuple[str, str | int | float]]
    | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">A list of string options to choose from. An option can also be a tuple of the form (name, value), where name is the displayed name of the dropdown choice and value is the value to be passed to the function, or returned by the function.</td>
</tr>

<tr>
<td align="left"><code>pipeline</code></td>
<td align="left" style="width: 25%;">

```python
pyannote.audio.core.pipeline.Pipeline | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">An instance of a pipeline to use. A value for this argument must be provied if `source` is set to `pipeline`.</td>
</tr>

<tr>
<td align="left"><code>value</code></td>
<td align="left" style="width: 25%;">

```python
str
    | int
    | float
    | list[str | int | float]
    | Callable
    | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">default value(s) selected in dropdown. If None, no value is selected by default. If callable, the function will be called whenever the app loads to set the initial value of the component.</td>
</tr>

<tr>
<td align="left"><code>source</code></td>
<td align="left" style="width: 25%;">

```python
"dropdown" | "instance"
```

</td>
<td align="left"><code>"dropdown"</code></td>
<td align="left">None</td>
</tr>

<tr>
<td align="left"><code>token</code></td>
<td align="left" style="width: 25%;">

```python
str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">None</td>
</tr>

<tr>
<td align="left"><code>allow_custom_value</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>False</code></td>
<td align="left">If True, allows user to enter a custom value that is not in the list of choices.</td>
</tr>

<tr>
<td align="left"><code>filterable</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If True, user will be able to type into the dropdown and filter the choices by typing. Can only be set to False if `allow_custom_value` is False.</td>
</tr>

<tr>
<td align="left"><code>label</code></td>
<td align="left" style="width: 25%;">

```python
str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">The label for this component. Appears above the component and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component is assigned to.</td>
</tr>

<tr>
<td align="left"><code>info</code></td>
<td align="left" style="width: 25%;">

```python
str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">additional component description.</td>
</tr>

<tr>
<td align="left"><code>every</code></td>
<td align="left" style="width: 25%;">

```python
float | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">If `value` is a callable, run the function 'every' number of seconds while the client connection is open. Has no effect otherwise. The event can be accessed (e.g. to cancel it) via this component's .load_event attribute.</td>
</tr>

<tr>
<td align="left"><code>show_label</code></td>
<td align="left" style="width: 25%;">

```python
bool | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">if True, will display label.</td>
</tr>

<tr>
<td align="left"><code>container</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If True, will place the component in a container - providing some extra padding around the border.</td>
</tr>

<tr>
<td align="left"><code>scale</code></td>
<td align="left" style="width: 25%;">

```python
int | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.</td>
</tr>

<tr>
<td align="left"><code>min_width</code></td>
<td align="left" style="width: 25%;">

```python
int
```

</td>
<td align="left"><code>160</code></td>
<td align="left">minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.</td>
</tr>

<tr>
<td align="left"><code>interactive</code></td>
<td align="left" style="width: 25%;">

```python
bool | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">if True, choices in this dropdown will be selectable; if False, selection will be disabled. If not provided, this is inferred based on whether the component is used as an input or output.</td>
</tr>

<tr>
<td align="left"><code>visible</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If False, component will be hidden.</td>
</tr>

<tr>
<td align="left"><code>elem_id</code></td>
<td align="left" style="width: 25%;">

```python
str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.</td>
</tr>

<tr>
<td align="left"><code>elem_classes</code></td>
<td align="left" style="width: 25%;">

```python
list[str] | str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.</td>
</tr>

<tr>
<td align="left"><code>render</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If False, component will not be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.</td>
</tr>
</tbody></table>


### Events

| name | description |
|:-----|:------------|
| `change` | Triggered when the value of the PipelineSelector changes either because of user input (e.g. a user types in a textbox) OR because of a function update (e.g. an image receives a value from the output of an event trigger). See `.input()` for a listener that is only triggered by user input. |
| `input` | This listener is triggered when the user changes the value of the PipelineSelector. |
| `select` | Event listener for when the user selects or deselects the PipelineSelector. Uses event data gradio.SelectData to carry `value` referring to the label of the PipelineSelector, and `selected` to refer to state of the PipelineSelector. See EventData documentation on how to use this event data |
| `focus` | This listener is triggered when the PipelineSelector is focused. |
| `blur` | This listener is triggered when the PipelineSelector is unfocused/blurred. |
| `key_up` | This listener is triggered when the user presses a key while the PipelineSelector is focused. |



### User function

The impact on the users predict function varies depending on whether the component is used as an input or output for an event (or both).

- When used as an Input, the component only impacts the input signature of the user function.
- When used as an output, the component only impacts the return signature of the user function.

The code snippet below is accurate in cases where the component is used as both an input and an output.

- **As output:** Is passed, an instanciated pipeline.
- **As input:** Should return, instanciated pipeline.

 ```python
 def predict(
     value: pyannote.audio.core.pipeline.Pipeline
 ) -> pyannote.audio.core.pipeline.Pipeline | None:
     return value
 ```
 
