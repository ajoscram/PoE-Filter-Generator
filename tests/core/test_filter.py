import builtins, pytest, os
from pytest import MonkeyPatch
from core.filter import _FILE_EXISTS_ERROR, _FILE_NOT_FOUND_ERROR, _PERMISSION_ERROR
from core import Filter, ExpectedError, Block, FILE_ENCODING
from test_utilities import FunctionMock, OpenMock

_INPUT_FILEPATH = "input_filepath"
_OUTPUT_FILEPATH = "output_filepath"
_LINES: list[str] = [ "line 1", "line 2" ]

def test_load_given_a_valid_filepath_should_return_a_filter(monkeypatch: MonkeyPatch):
    open_mock = OpenMock(monkeypatch, _LINES)

    filter = Filter.load(_INPUT_FILEPATH)

    assert open_mock.received(_INPUT_FILEPATH, "r", encoding=FILE_ENCODING)
    assert filter.filepath == _INPUT_FILEPATH
    assert [ str(line) for line in filter.blocks[0].lines ] == _LINES

_OPEN_FILE_EXCEPTIONS = [ (FileNotFoundError, _FILE_NOT_FOUND_ERROR), (PermissionError, _PERMISSION_ERROR) ]
@pytest.mark.parametrize("error_to_raise, error_message", _OPEN_FILE_EXCEPTIONS)
def test_load_given_file_is_not_found_should_raise(
    monkeypatch: MonkeyPatch, error_to_raise: Exception, error_message: str):
    _ = FunctionMock(monkeypatch, builtins.open, error_to_raise)

    with pytest.raises(ExpectedError) as error:
        _ = Filter.load(_INPUT_FILEPATH)
    
    assert error.value.message == error_message
    assert error.value.filepath == _INPUT_FILEPATH

def test_save_should_save_the_lines_in_the_filter(monkeypatch: MonkeyPatch):
    DIRECTORY = "directory"
    FILTER = Filter(_INPUT_FILEPATH, Block.extract(_LINES))
    open_mock = OpenMock(monkeypatch, _LINES)
    dirname_mock = FunctionMock(monkeypatch, os.path.dirname, DIRECTORY)
    makedirs_mock = FunctionMock(monkeypatch, os.makedirs)

    FILTER.save(_OUTPUT_FILEPATH)

    assert dirname_mock.received(_OUTPUT_FILEPATH)
    assert makedirs_mock.received(DIRECTORY, exist_ok=True)
    assert open_mock.received(_OUTPUT_FILEPATH, "w", encoding=FILE_ENCODING)
    assert open_mock.file.got_written(str(FILTER.blocks[0]))

_WRITE_FILE_EXCEPTIONS = [ (FileExistsError, _FILE_EXISTS_ERROR), (PermissionError, _PERMISSION_ERROR) ]
@pytest.mark.parametrize("exception_to_raise, error_message", _WRITE_FILE_EXCEPTIONS)
def test_save_given_the_file_exists_and_cannot_be_overwritten_should_raise(
    monkeypatch: MonkeyPatch, exception_to_raise: Exception, error_message: str):
    
    _ = FunctionMock(monkeypatch, os.path.dirname, "")
    _ = FunctionMock(monkeypatch, builtins.open, exception_to_raise)
    filter = Filter(_INPUT_FILEPATH, Block.extract(_LINES))

    with pytest.raises(ExpectedError) as error:
        filter.save(_OUTPUT_FILEPATH)

    assert error.value.message == error_message
    assert error.value.filepath == _OUTPUT_FILEPATH