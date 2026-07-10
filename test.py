from abc import ABC
from dataclasses import dataclass
from enum import StrEnum
import re

class _Splitter(StrEnum):
    ROOT = "|"
    BLOCKNAME = "->"
    TEMPLATE = "{"

@dataclass
class _ImportSegment(ABC):
    name: str
    regex: str
    allows_empty: bool = False

@dataclass
class _NamedImportSegment(_ImportSegment):
    def __init__(self, name: str , regex: str):
        super().__init__(name, regex.format(name=name))

class _SplitterImportSegment(_ImportSegment):
    def __init__(self, splitter: _Splitter, regex: str, allows_empty: bool = False):
        super().__init__(
            splitter.name.lower(),
            regex.format(name=splitter.name.lower(), splitter=splitter.value),
            allows_empty)

_ROOT_SEGMENT = _SplitterImportSegment(_Splitter.ROOT, r"(?:(?P<{name}>.*?)\s*\{splitter})")
_NAVIGATION_SEGMENT = _NamedImportSegment("navigation", r"(?P<{name}>.*?)")
_BLOCKNAME_SEGMENT = _SplitterImportSegment(_Splitter.BLOCKNAME, r"(?:{splitter}\s*(?P<{name}>.*?))")
_TEMPLATE_SEGMENT = _SplitterImportSegment(_Splitter.TEMPLATE, r"(?:{splitter}\s*(?P<{name}>.*?))")
_IMPORT_REGEX = fr"^\s*{_ROOT_SEGMENT.regex}?\s*{_NAVIGATION_SEGMENT.regex}\s*{_BLOCKNAME_SEGMENT.regex}?\s*{_TEMPLATE_SEGMENT.regex}?\s*$"

text = "dfgsdfg | dfgdfg |"

match = re.search(_IMPORT_REGEX, text)

root = match.group(_ROOT_SEGMENT.name)
navigation = match.group(_NAVIGATION_SEGMENT.name)
blockname = match.group(_BLOCKNAME_SEGMENT.name)
templates_text = match.group(_TEMPLATE_SEGMENT.name)

print(f"'{root}'")
print(f"'{navigation}'")
print(f"'{blockname}'")
print(f"'{templates_text}'")
