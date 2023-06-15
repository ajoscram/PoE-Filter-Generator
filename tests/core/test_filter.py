import builtins, pytest, os
from pytest import MonkeyPatch
from core.filter import _FILE_EXISTS_ERROR, _FILE_NOT_FOUND_ERROR, _PERMISSION_ERROR
from core import Filter, GeneratorError, Block
from test_utilities import FunctionMock

_FILEPATH = "filepath"
_LINES: list[str] = [ "line 1", "line 2" ]

class _MockFile:
    written_text: str = None

    def readlines(self):
        return _LINES
    
    def write(self, text: str):
        self.written_text = text
    
    def __enter__(self):
        return self
    
    def __exit__(self, _, __, ___):
        return self

def test_load_given_a_valid_filepath_should_return_a_filter(monkeypatch: MonkeyPatch):
    MOCK_FILE = _MockFile()
    open_mock = FunctionMock(monkeypatch, builtins.open, MOCK_FILE)

    filter = Filter.load(_FILEPATH)

    assert open_mock.received(_FILEPATH, "r")
    assert filter.filepath == _FILEPATH
    assert [ str(line) for line in filter.blocks[0].lines ] == _LINES

_OPEN_FILE_EXCEPTIONS = [ (FileNotFoundError, _FILE_NOT_FOUND_ERROR), (PermissionError, _PERMISSION_ERROR) ]
@pytest.mark.parametrize("error_to_raise, error_message", _OPEN_FILE_EXCEPTIONS)
def test_load_given_file_is_not_found_should_raise(
    monkeypatch: MonkeyPatch, error_to_raise: Exception, error_message: str):
    _ = FunctionMock(monkeypatch, builtins.open, error_to_raise)

    with pytest.raises(GeneratorError) as error:
        _ = Filter.load(_FILEPATH)
    
    assert error.value.message == error_message
    assert error.value.filepath == _FILEPATH

def test_save_should_save_the_lines_in_the_filter(monkeypatch: MonkeyPatch):
    DIRECTORY = "directory"
    MOCK_FILE = _MockFile()
    FILTER = Filter(_FILEPATH, Block.extract(_LINES))
    dirname_mock = FunctionMock(monkeypatch, os.path.dirname, DIRECTORY)
    makedirs_mock = FunctionMock(monkeypatch, os.makedirs)
    open_mock = FunctionMock(monkeypatch, builtins.open, MOCK_FILE)

    FILTER.save()

    assert dirname_mock.received(_FILEPATH)
    assert makedirs_mock.received(DIRECTORY, exist_ok=True)
    assert open_mock.received(_FILEPATH, "w")
    assert MOCK_FILE.written_text == str(FILTER.blocks[0])

_WRITE_FILE_EXCEPTIONS = [ (FileExistsError, _FILE_EXISTS_ERROR), (PermissionError, _PERMISSION_ERROR) ]
@pytest.mark.parametrize("exception_to_raise, error_message", _WRITE_FILE_EXCEPTIONS)
def test_save_given_the_file_exists_and_cannot_be_overwritten_should_raise(
    monkeypatch: MonkeyPatch, exception_to_raise: Exception, error_message: str):
    _ = FunctionMock(monkeypatch, os.path.dirname, "")
    _ = FunctionMock(monkeypatch, builtins.open, exception_to_raise)
    filter = Filter(_FILEPATH, Block.extract(_LINES))

    with pytest.raises(GeneratorError) as error:
        filter.save()

    assert error.value.message == error_message
    assert error.value.filepath == _FILEPATH