"""Module that exports the HandlerError class only. Every handler exception should be a subclass of HandlerError."""

class HandlerError(Exception):
    """Class for handler exceptions. Every handler exception should be a subclass of this class."""

    def has_line_number(self):
        return self.line_number != None

    def __init__(self, line_number: int, message: str):
        """Takes a message from the caller and a line number where the error occurred."""
        self.message = message
        self.line_number = line_number