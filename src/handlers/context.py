from core import Filter

class Context:
    """A container for several contextual clues passed to Handlers."""
    def __init__(self, filter: Filter, options: list[str]):
        self.filter = filter
        self.options = options