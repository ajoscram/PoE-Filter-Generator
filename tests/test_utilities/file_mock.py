import builtins
from pytest import MonkeyPatch
from .function_mock import FunctionMock

class FileMock:
    """This class monkeypatches the built-in `open` with this object function and mocks common file operations."""

    def __init__(self, monkeypatch: MonkeyPatch, line_or_lines: str | list[str] = []):
        """`line_or_lines` corresponds to the lines returned when the file is read."""
        self.lines = [ line_or_lines ] if isinstance(line_or_lines, str) else line_or_lines
        self._written_values = []
        self._open_mock = FunctionMock(monkeypatch, builtins.open, self)

    def opened_with(self, filepath: str, mode: str):
        """Validates the `open` built-in function was called with the `filepath` and `mode` returned."""
        return self._open_mock.received(filepath, mode)
    
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