from dataclasses import dataclass
from core import Filter

@dataclass
class Context:
    """A container for several contextual clues passed to Handlers."""
    filter: Filter
    options: list[str]