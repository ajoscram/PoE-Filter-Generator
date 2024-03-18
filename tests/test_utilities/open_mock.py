import builtins
from pytest import MonkeyPatch
from .function_mock import FunctionMock

class OpenMock(FunctionMock):
    """This class monkeypatches the built-in `open` function with this object and mocks common file operations."""

    def __init__(self, monkeypatch: MonkeyPatch, line_or_lines: str | list[str] = []):
        """`line_or_lines` corresponds to the lines returned when the file is read."""
        self.file = FileMock(line_or_lines)
        super().__init__(monkeypatch, builtins.open, self.file)

class FileMock:
    """This class represents a file object opened with the `open` function."""

    def __init__(self, line_or_lines: str | list[str] = []):
        """`line_or_lines` corresponds to the lines returned when the file is read."""
        self.lines = [ line_or_lines ] if isinstance(line_or_lines, str) else line_or_lines
        self._written_values = []
    
    def got_written(self, value):
        """Returns `True` if `value` got written to the file mock. `False` otherwise."""
        return any(value == written_value for written_value in self._written_values)

    def readlines(self):
        return self.lines
    
    def read(self):
        return "".join(self.lines)
    
    def write(self, value):
        self._written_values += [ value ]
    
    def flush(self):
        pass
    
    def fileno(self):
        return 1
    
    def __enter__(self):
        return self
    
    def __exit__(self, _, __, ___):
        return self