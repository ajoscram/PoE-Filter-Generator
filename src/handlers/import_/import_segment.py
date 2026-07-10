from abc import ABC
from dataclasses import dataclass
from .constants import Splitter

@dataclass
class ImportSegment(ABC):
    name: str
    regex: str
    allows_empty: bool = False

@dataclass
class NamedImportSegment(ImportSegment):
    def __init__(self, name: str , regex: str):
        super().__init__(name, regex.format(name=name), allows_empty=True)

class SplitterImportSegment(ImportSegment):
    def __init__(self, splitter: Splitter, regex: str, allows_empty: bool = False):
        super().__init__(
            splitter.name.lower(),
            regex.format(name=splitter.name.lower(), splitter=splitter.value),
            allows_empty)