from typing import ClassVar, Dict, List, Optional, Text

import networkx as nx
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
    # css style level of the annotation
    level: Optional[int]
    # total num level
    num_levels: Optional[int]

    def __init__(
        self,
        start: float,
        end: float,
        speaker: Text,
        level: Optional[int] = None,
        num_levels: Optional[int] = None,
        **kwargs,
    ):
        super().__init__(
            start=start,
            end=end,
            speaker=speaker,
            level=level,
            num_levels=num_levels,
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

    def _prepare_annotations(self, annotations) -> List[Annotation]:

        prepared_annotations: List[Annotation] = []

        # compute overlap graph (one node per annotation, edges between overlapping regions)
        overlap_graph = nx.Graph()
        for (s1, t1), (s2, t2) in annotations.co_iter(annotations):
            overlap_graph.add_edge((s1, t1), (s2, t2))

        # solve the graph coloring problem for each connected subgraph and
        # use the solution for annotations layout
        for sub_graph in nx.connected_components(overlap_graph):
            sub_coloring = nx.coloring.greedy_color(
                overlap_graph.subgraph(sorted(sub_graph))
            )

            num_colors = max(sub_coloring.values()) + 1
            for (segment, annotation_id), color in sub_coloring.items():
                # assumes that no more than 4 annotations can overlap at any given time
                level = (color % 4 if num_colors > 4 else color) + 1
                num_levels = 4 if num_colors > 4 else num_colors

                prepared_annotations.append(
                    Annotation(
                        start=segment.start,
                        end=segment.end,
                        speaker=annotations[segment, annotation_id],
                        level=level,
                        num_levels=num_levels,
                    )
                )
        return prepared_annotations
