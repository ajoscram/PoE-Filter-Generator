class Invocation:
    """Represents a handler invocation via the command line."""
    def __init__(self, handler_name: str):
        self.handler_name = handler_name
        self.options: list[str] = []