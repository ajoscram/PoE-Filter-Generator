class Invocation:
    """The invocation class represents a handler invocation."""
    def __init__(self, handler_name: str):
        self.handler_name = handler_name
        self.options: list[str] = []