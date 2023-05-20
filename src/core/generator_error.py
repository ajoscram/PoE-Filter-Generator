class GeneratorError(Exception):
    """
    Represents an error that occurred while generating the output filter.
    This exception should be used when displaying expected errors to users in handlers.
    """
    def __init__(self, message: str, line_number: int = None, filepath: str = None):
        """
        * `message`: the message to display as an error.
        * `line_number`: the line number in the filter where the error happened.
        * `filepath`: The filepath to the filter's where the error happened.
        """
        self.message: str = message
        self.filepath: str = filepath
        self.line_number: int = line_number
    
    def __str__(self):
        result = self.message
        result += "\n" if self.line_number or self.filepath else ""
        result += f"\n\tOn file: {self.filepath}" if self.filepath else ""
        result += f"\n\tOn line: {self.line_number}" if self.line_number else ""
        return result
