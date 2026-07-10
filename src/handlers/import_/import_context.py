import utils
from dataclasses import dataclass, field
from core import Filter
from .import_ import Import
from ..context import Context

@dataclass
class ImportContext(Context):
    """Represents a Context used by the .import handler."""
    roots: dict[str, str] = None
    cache: dict[str, Filter] = field(default_factory=dict[str, Filter])
    imports: list[Import] = field(default_factory=list[Import])

    def __post_init__(self):
        if self.roots is None:
            self.roots = { name: value
                for name, value in utils.parse_key_value_list(" ".join(self.options)) }
    
    @property
    def current_filepath(self):
        return self.imports[-1].filepath
    
    @property
    def original_filepath(self):
        return self.imports[0].filepath
    
    def clone(self, new_import: Import):
        return ImportContext(
            self.filter,
            self.options,
            self.roots,
            self.cache,
            self.imports + [new_import])