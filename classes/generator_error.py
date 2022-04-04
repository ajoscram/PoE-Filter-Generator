"""Module that exports the GeneratorError class only."""

class GeneratorError(Exception):
    def __init__(self, message: str, line_number: int = None, filepath: str = None):
        self.message = message
        self.filepath = filepath
        self.line_number = line_number
    
    def __str__(self):
        result = self.message
        result += "" if not self.filepath else f"\n\n\tOn file: {self.filepath}"
        result += "" if not self.line_number else f"\n\n\tOn line: {self.line_number}"
        return result
