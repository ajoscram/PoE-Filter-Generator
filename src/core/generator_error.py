class GeneratorError(Exception):
    def __init__(self, message: str, line_number: int = None, filepath: str = None):
        self.message: str = message
        self.filepath: str = filepath
        self.line_number: int = line_number
    
    def __str__(self):
        result = self.message
        result += "\n" if self.line_number or self.filepath else ""
        result += f"\n\tOn file: {self.filepath}" if self.filepath else ""
        result += f"\n\tOn line: {self.line_number}" if self.line_number else ""
        return result
