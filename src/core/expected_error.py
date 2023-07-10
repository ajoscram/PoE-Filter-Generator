class ExpectedError(Exception):
    """
    Represents an error that occurred during execution which is expected.
    Always raise these errors if applicable.
    """
    def __init__(self, message: str, line_number: int = None, filepath: str = None):
        """
        * `message`: the message to display as an error.
        * `line_number`: the file line number where the error happened, if applicable.
        * `filepath`: The filepath where the error happened, if applicable.
        """
        self.message = message
        self.filepath = filepath
        self.line_number = line_number
    
    def __str__(self):
        result = self.message
        result += "\n" if self.line_number or self.filepath else ""
        result += f"\n\tOn file: {self.filepath}" if self.filepath else ""
        result += f"\n\tOn line: {self.line_number}" if self.line_number else ""
        return result