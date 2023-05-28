import builtins, pytest, os
from pytest import MonkeyPatch
from src.core.filter import _FILE_EXISTS_ERROR, _FILE_NOT_FOUND_ERROR, _PERMISSION_ERROR
from src.core import Filter, GeneratorError, Block

FILEPATH = "filepath"
LINES: list[str] = [ "line 1", "line 2" ]

class MockFile:
    written_text: str = None
    filepath: str = None
    open_mode: str = None

    def readlines(self):
        return LINES
    
    def write(self, text: str):
        self.written_text = text
    
    def __enter__(self):
        return self
    
    def __exit__(self, _, __, ___):
        return self

class DirectoryInfo:
    filepath: str
    directory: str
    exist_ok: bool

def test_load_given_a_valid_filepath_should_return_a_filter(monkeypatch: MonkeyPatch):
    mock_file = MockFile()
    def mock_open(filepath: str, open_mode: str):
        mock_file.filepath = filepath
        mock_file.open_mode = open_mode
        return mock_file
    monkeypatch.setattr(builtins, "open", mock_open)

    filter = Filter.load(FILEPATH)

    assert mock_file.filepath == FILEPATH
    assert mock_file.open_mode == "r"
    assert filter.filepath == FILEPATH
    assert [ str(line) for line in filter.blocks[0].lines ] == LINES

OPEN_FILE_EXCEPTIONS = [ (FileNotFoundError, _FILE_NOT_FOUND_ERROR), (PermissionError, _PERMISSION_ERROR) ]
@pytest.mark.parametrize("exception_to_raise, error_message", OPEN_FILE_EXCEPTIONS)
def test_load_given_file_is_not_found_should_raise(
    monkeypatch: MonkeyPatch, exception_to_raise: Exception, error_message: str):
    def mock_open(_, __): raise exception_to_raise
    monkeypatch.setattr(builtins, "open", mock_open)

    with pytest.raises(GeneratorError) as error:
        _ = Filter.load(FILEPATH)
    
    assert error.value.message == error_message
    assert error.value.filepath == FILEPATH

def test_save_should_save_the_lines_in_the_filter(monkeypatch: MonkeyPatch):
    DIRECTORY = "directory"
    directory_info = DirectoryInfo()
    
    def dirname(filepath: str):
        directory_info.filepath = filepath
        return DIRECTORY
    monkeypatch.setattr(os.path, "dirname", dirname)
    
    def makedirs(directory: str, exist_ok: bool):
        directory_info.directory = directory
        directory_info.exist_ok = exist_ok
    monkeypatch.setattr(os, "makedirs", makedirs)
    
    mock_file = MockFile()
    def mock_open(filepath: str, open_mode: str):
        mock_file.filepath = filepath
        mock_file.open_mode = open_mode
        return mock_file
    monkeypatch.setattr(builtins, "open", mock_open)
    
    filter = Filter(FILEPATH, Block.extract(LINES, 1))

    filter.save()

    assert directory_info.filepath == FILEPATH
    assert directory_info.directory == DIRECTORY
    assert directory_info.exist_ok == True
    assert mock_file.filepath == FILEPATH
    assert mock_file.open_mode == "w"
    assert mock_file.written_text == str(filter.blocks[0])

WRITE_FILE_EXCEPTIONS = [ (FileExistsError, _FILE_EXISTS_ERROR), (PermissionError, _PERMISSION_ERROR) ]
@pytest.mark.parametrize("exception_to_raise, error_message", WRITE_FILE_EXCEPTIONS)
def test_save_given_the_file_exists_and_cannot_be_overwritten_should_raise(
    monkeypatch: MonkeyPatch, exception_to_raise: Exception, error_message: str):
    def mock_open(_, __): raise exception_to_raise
    monkeypatch.setattr(builtins, "open", mock_open)
    monkeypatch.setattr(os.path, "dirname", lambda _: "")
    filter = Filter(FILEPATH, Block.extract(LINES, 1))

    with pytest.raises(GeneratorError) as error:
        filter.save()

    assert error.value.message == error_message
    assert error.value.filepath == FILEPATH