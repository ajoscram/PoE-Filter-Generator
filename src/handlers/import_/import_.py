import os
from dataclasses import dataclass, field
from .constants import Splitter

@dataclass
class Import:
    filepath: str
    blockname: str | None
    templates: dict[str, str] = field(default_factory=dict[str, str])

    def __eq__(self, other):
        if not isinstance(other, Import):
            return False

        equivalent_filepath = os.path.samefile(self.filepath, other.filepath)
        same_block = self.blockname == other.blockname
        return equivalent_filepath and same_block

    def __str__(self):
        string = self.filepath
        string += f" {Splitter.BLOCKNAME} " + self.blockname if self.blockname is not None else ""
        return string