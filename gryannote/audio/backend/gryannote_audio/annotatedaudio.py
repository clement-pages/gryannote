"""gr.Audio() component."""

from __future__ import annotations

import dataclasses
from pathlib import Path
from typing import Any, Callable, Literal, Tuple

import httpx
import numpy as np
from gradio import processing_utils, utils
from gradio.components.base import Component, StreamingInput, StreamingOutput
from gradio.data_classes import FileData
from gradio.events import Events
from gradio.exceptions import Error
from gradio_client import utils as client_utils
from gradio_client.documentation import document, set_documentation_group
from pyannote.core import Annotation as PyannoteAnnotation

from .core import AnnotadedAudioData

set_documentation_group("component")


@dataclasses.dataclass
class WaveformOptions:
    """
    A dataclass for specifying options for the waveform display in the AnnotatedAudio component. An instance of this class can be passed into the `waveform_options` parameter of `AnnotatedAudio`.
    Parameters:
        waveform_color: The color (as a hex string or valid CSS color) of the full waveform representing the amplitude of the audio. Defaults to a light gray color.
        waveform_progress_color: The color (as a hex string or valid CSS color) that the waveform fills with to as the audio plays. Defaults to an orange color.
        show_recording_waveform: Whether to show the waveform when recording audio. Defaults to True.
        show_controls: Whether to show the standard HTML audio player below the waveform when recording audio or playing recorded audio. Defaults to False.
        skip_length: The percentage (between 0 and 100) of the audio to skip when clicking on the skip forward / skip backward buttons. Defaults to 5.
        sample_rate: The output sample rate (in Hz) of the audio after editing. Defaults to 44100.
    """

    waveform_color: str = "#9ca3af"
    waveform_progress_color: str = "#f97316"
    show_recording_waveform: bool = True
    show_controls: bool = False
    skip_length: int | float = 5
    sample_rate: int = 44100


@document()
class AnnotatedAudio(
    StreamingInput,
    StreamingOutput,
    Component,
):
    """
    Creates an audio component that can be used to upload/record audio (as an input) or display audio (as an output).
    Preprocessing: passes the uploaded audio as a {Tuple(int, numpy.array)} corresponding to (sample rate in Hz, audio data as a 16-bit int array whose values range from -32768 to 32767), or as a {str} filepath, depending on `type`.
    Postprocessing: expects a {Tuple(int, numpy.array)} corresponding to (sample rate in Hz, audio data as a float or int numpy array) or as a {str} or {pathlib.Path} filepath or URL to an audio file, or bytes for binary content (recommended for streaming). Note: When converting audio data from float format to WAV, the audio is normalized by its peak value to avoid distortion or clipping in the resulting audio.
    Examples-format: a {str} filepath to a local file that contains audio.
    Demos: main_note, generate_tone, reverse_audio
    Guides: real-time-speech-recognition
    """

    EVENTS = [
        Events.stream,
        Events.change,
        Events.clear,
        Events.play,
        Events.pause,
        Events.stop,
        Events.pause,
        Events.start_recording,
        Events.pause_recording,
        Events.stop_recording,
        Events.upload,
        Events.edit,
    ]

    data_model = AnnotadedAudioData

    def __init__(
        self,
        value: Tuple[str | Path | Tuple[int, np.ndarray], PyannoteAnnotation]
        | Callable
        | None = None,
        *,
        sources: list[Literal["upload", "microphone"]] | None = None,
        type: Literal["numpy", "filepath"] = "numpy",
        label: str | None = None,
        every: float | None = None,
        show_label: bool | None = None,
        container: bool = True,
        scale: int | None = None,
        min_width: int = 160,
        interactive: bool | None = None,
        visible: bool = True,
        streaming: bool = False,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        format: Literal["wav", "mp3"] = "wav",
        autoplay: bool = False,
        show_download_button=True,
        show_share_button: bool | None = None,
        editable: bool = True,
        min_length: int | None = None,
        max_length: int | None = None,
        waveform_options: WaveformOptions | dict | None = None,
    ):
        """
        Parameters:
            value: A [audio path, pyannote annotations] tuple for the default value that AnnotatedAudio component is going to take. If callable, the function will be called whenever the app loads to set the initial value of the component.
            sources: A list of sources permitted for audio. "upload" creates a box where user can drop an audio file, "microphone" creates a microphone input. The first element in the list will be used as the default source. If None, defaults to ["upload", "microphone"], or ["microphone"] if `streaming` is True.
            type: The format the audio file is converted to before being passed into the prediction function. "numpy" converts the audio to a tuple consisting of: (int sample rate, numpy.array for the data), "filepath" passes a str path to a temporary file containing the audio.
            label: The label for this component. Appears above the component and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component is assigned to.
            every: If `value` is a callable, run the function 'every' number of seconds while the client connection is open. Has no effect otherwise. Queue must be enabled. The event can be accessed (e.g. to cancel it) via this component's .load_event attribute.
            show_label: if True, will display label.
            container: If True, will place the component in a container - providing some extra padding around the border.
            scale: relative width compared to adjacent Components in a Row. For example, if Component A has scale=2, and Component B has scale=1, A will be twice as wide as B. Should be an integer.
            min_width: minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.
            interactive: If True, will allow users to upload and edit an audio file. If False, can only be used to play audio. If not provided, this is inferred based on whether the component is used as an input or output.
            visible: If False, component will be hidden.
            streaming: If set to True when used in a `live` interface as an input, will automatically stream webcam feed. When used set as an output, takes audio chunks yield from the backend and combines them into one streaming audio output.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            format: The file format to save audio files. Either 'wav' or 'mp3'. wav files are lossless but will tend to be larger files. mp3 files tend to be smaller. Default is wav. Applies both when this component is used as an input (when `type` is "format") and when this component is used as an output.
            autoplay: Whether to automatically play the audio when the component is used as an output. Note: browsers will not autoplay audio files if the user has not interacted with the page yet.
            show_download_button: If True, will show a download button in the corner of the component for saving audio. If False, icon does not appear.
            show_share_button: If True, will show a share icon in the corner of the component that allows user to share outputs to Hugging Face Spaces Discussions. If False, icon does not appear. If set to None (default behavior), then the icon appears if this Gradio app is launched on Spaces, but not otherwise.
            editable: If True, allows users to manipulate the audio file (if the component is interactive).
            min_length: The minimum length of audio (in seconds) that the user can pass into the prediction function. If None, there is no minimum length.
            max_length: The maximum length of audio (in seconds) that the user can pass into the prediction function. If None, there is no maximum length.
            waveform_options: A dictionary of options for the waveform display. Options include: waveform_color (str), waveform_progress_color (str), show_controls (bool), skip_length (int). Default is None, which uses the default values for these options.
        """
        valid_sources: list[Literal["upload", "microphone"]] = ["upload", "microphone"]
        if sources is None:
            self.sources = ["microphone"] if streaming else valid_sources
        elif isinstance(sources, str) and sources in valid_sources:
            self.sources = [sources]
        elif isinstance(sources, list):
            self.sources = sources
        else:
            raise ValueError(
                f"`sources` must be a list consisting of elements in {valid_sources}"
            )
        for source in self.sources:
            if source not in valid_sources:
                raise ValueError(
                    f"`sources` must a list consisting of elements in {valid_sources}"
                )
        valid_types = ["numpy", "filepath"]
        if type not in valid_types:
            raise ValueError(
                f"Invalid value for parameter `type`: {type}. Please choose from one of: {valid_types}"
            )
        self.type = type
        self.streaming = streaming
        if self.streaming and "microphone" not in self.sources:
            raise ValueError(
                "AnnotatedAudio streaming only available if sources includes 'microphone'."
            )
        self.format = format
        self.autoplay = autoplay
        self.show_download_button = show_download_button
        self.show_share_button = (
            (utils.get_space() is not None)
            if show_share_button is None
            else show_share_button
        )
        self.editable = editable
        if waveform_options is None:
            self.waveform_options = WaveformOptions()
        self.waveform_options = (
            WaveformOptions(**waveform_options)
            if isinstance(waveform_options, dict)
            else waveform_options
        )
        self.min_length = min_length
        self.max_length = max_length

        super().__init__(
            label=label,
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
        return "https://github.com/gradio-app/gradio/raw/main/test/test_files/audio_sample.wav"

    def preprocess(
        self, payload: AnnotadedAudioData | None
    ) -> Tuple[int, np.ndarray] | str | None:
        if payload is None:
            return payload

        file_data = payload.file_data

        assert file_data.path
        # Need a unique name for the file to avoid re-using the same audio file if
        # a user submits the same audio file twice
        temp_file_path = Path(file_data.path)
        output_file_name = str(
            temp_file_path.with_name(f"{temp_file_path.stem}{temp_file_path.suffix}")
        )

        sample_rate, data = processing_utils.audio_from_file(temp_file_path)

        duration = len(data) / sample_rate
        if self.min_length is not None and duration < self.min_length:
            raise Error(
                f"Audio is too short, and must be at least {self.min_length} seconds"
            )
        if self.max_length is not None and duration > self.max_length:
            raise Error(
                f"Audio is too long, and must be at most {self.max_length} seconds"
            )

        if self.type == "numpy":
            return (sample_rate, data)
        elif self.type == "filepath":
            output_file = str(Path(output_file_name).with_suffix(f".{self.format}"))
            processing_utils.audio_to_file(
                sample_rate, data, output_file, format=self.format
            )
            return output_file
        else:
            raise ValueError(
                "Unknown type: "
                + str(self.type)
                + ". Please choose from: 'numpy', 'filepath'."
            )

    def postprocess(
        self, value: Tuple[str | Path | Tuple[int, np.ndarray], PyannoteAnnotation]
    ) -> AnnotadedAudioData | None:
        """
        Parameters:
            value: a tuble containing two elements :
                - an audio file representing the audio downloaded by the user. The audio file can
                be a file path (Path or str) or a tuple of (sample_rate, data).
                - a pyannote Annotation object containing annotation provided by the pipeline
        Returns:
            an audio data object. This object contains file data and a list of diarization annotations
        """
        orig_name = None
        if value is None:
            return None

        audio, annotations = value

        # postprocess audio
        if isinstance(audio, bytes):
            if self.streaming:
                return value
            audio_path = Path(
                processing_utils.save_bytes_to_cache(
                    audio, "audio", cache_dir=self.GRADIO_CACHE
                )
            )
            orig_name = audio_path.name

        elif isinstance(audio, Tuple):
            sample_rate, data = audio
            audio_path = Path(
                processing_utils.save_audio_to_cache(
                    data, sample_rate, format=self.format, cache_dir=self.GRADIO_CACHE
                )
            )
            orig_name = audio_path.name

        else:
            if not isinstance(audio, (str, Path)):
                raise ValueError(f"Cannot process {audio} as FileData")
            audio_path = Path(audio)
            orig_name = audio_path.name if audio_path.exists() else None

        file_data = FileData(path=str(audio_path), orig_name=orig_name)

        return AnnotadedAudioData(file_data=file_data, annotations=annotations)

    def stream_output(
        self, value, output_id: str, first_chunk: bool
    ) -> Tuple[bytes | None, Any]:
        output_file = {
            "path": output_id,
            "is_stream": True,
        }
        if value is None:
            return None, output_file
        if isinstance(value, bytes):
            return value, output_file
        if client_utils.is_http_url_like(value["path"]):
            response = httpx.get(value["path"])
            binary_data = response.content
        else:
            output_file["orig_name"] = value["orig_name"]
            file_path = value["path"]
            is_wav = file_path.endswith(".wav")
            with open(file_path, "rb") as f:
                binary_data = f.read()
            if is_wav:
                # strip length information from first chunk header, remove headers entirely from subsequent chunks
                if first_chunk:
                    binary_data = (
                        binary_data[:4] + b"\xFF\xFF\xFF\xFF" + binary_data[8:]
                    )
                    binary_data = (
                        binary_data[:40] + b"\xFF\xFF\xFF\xFF" + binary_data[44:]
                    )
                else:
                    binary_data = binary_data[44:]
        return binary_data, output_file

    def process_example(
        self, value: Tuple[int, np.ndarray] | str | Path | bytes | None
    ) -> str:
        if value is None:
            return ""
        elif isinstance(value, (str, Path)):
            return Path(value).name
        return "(audio)"

    def check_streamable(self):
        if (
            self.sources is not None
            and "microphone" not in self.sources
            and self.streaming
        ):
            raise ValueError(
                "AnnotatedAudio streaming only available if source includes 'microphone'."
            )
