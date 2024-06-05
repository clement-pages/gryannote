from typing import ClassVar, Dict, List, Optional, Text

from gradio.data_classes import FileData, GradioModel
from pyannote.core import Annotation as PyannoteAnnotation


class Annotation(GradioModel):
    # each speaker is assigned a color
    speakers_color: ClassVar[Dict] = {}

    # beginning of the annotation, in seconds
    start: float
    # end of the annotation, in seconds
    end: float
    # annotation speaker label
    speaker: Text

    def __init__(
        self,
        start: float,
        end: float,
        speaker: Text,
        **kwargs,
    ):
        super().__init__(
            start=start,
            end=end,
            speaker=speaker,
        )


class AnnotadedAudioData(GradioModel):
    file_data: FileData
    annotations: Optional[List[Annotation]] = None

    def __init__(
        self,
        file_data: FileData,
        annotations: Optional[PyannoteAnnotation | List[Annotation]] = None,
        **kwargs,
    ):

        if isinstance(annotations, PyannoteAnnotation):
            annotations = self._prepare_annotations(annotations)

        super().__init__(
            file_data=file_data,
            annotations=annotations,
            **kwargs,
        )

    def _prepare_annotations(self, annotations: List[PyannoteAnnotation]) -> List[Annotation]:

        prepared_annotations: List[Annotation] = []

        for segment, _ , label in annotations.itertrack(yield_label=True) :
            prepared_annotations.append(
                Annotation(
                    start=segment.start,
                    end=segment.end,
                    speaker=label,
                )
            )
        return prepared_annotations
