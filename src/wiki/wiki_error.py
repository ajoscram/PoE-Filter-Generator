class WikiError(Exception):
    """Represents an error that occurred during a Wiki query."""
    def __init__(self, message: str):
        """* `message`: The error message to display."""
        self.message = message
    def __str__(self):
        return self.message