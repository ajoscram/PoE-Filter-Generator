"""Module that exports the GeneratorError class only."""

class GeneratorError(Exception):
    def __init__(self, message: str, line_number: int = None, filepath: str = None):
        self.message: str = message
        self.filepath: str = filepath
        self.line_number: int = line_number
    
    def __str__(self):
        result = f"{self.message}\n"
        result += "" if not self.filepath else f"\n\tOn file: {self.filepath}"
        result += "" if not self.line_number else f"\n\tOn line: {self.line_number}"
        return result
