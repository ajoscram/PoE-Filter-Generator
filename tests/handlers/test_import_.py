import os, pytest
from pytest import MonkeyPatch
from core import ExpectedError, Filter, Operand, RULE_START
from handlers import import_
from handlers.import_ import _BLOCK_NAME, _BLOCK_NAME_ERROR_TEXT, _BLOCK_NOT_FOUND_ERROR, _CIRCULAR_REFERENCE_ERROR, _EMPTY_PARAMETER_ERROR, _FILTER_DOES_NOT_EXIST_ERROR, _FILTER_EXTENSION, _INCORRECT_RULE_FORMAT_ERROR, _LINE_PATTERN_NOT_FOUND_ERROR, _LINE_PATTERN_ERROR_TEXT, _LOOP_REPEATS_HERE_ERROR_TEXT, _LOOP_STARTS_HERE_ERROR_TEXT, _SPLITTER, NAME as IMPORT
from test_utilities import create_filter, FunctionMock

_TARGET_BLOCK_NAME = "block_name"
_TARGET_BLOCK_CONTENTS = "block contents here"

@pytest.fixture(autouse=True)
def setup(monkeypatch: MonkeyPatch):
    import_._filter_cache = {}
    _ = FunctionMock(monkeypatch, os.path.normpath, lambda x: x)
    _ = FunctionMock(monkeypatch, os.path.samefile, lambda x, y: x == y)
    _ = FunctionMock(monkeypatch, os.path.abspath, lambda x: x)

@pytest.fixture(autouse=True)
def dirname_mock(monkeypatch: MonkeyPatch):
    return FunctionMock(monkeypatch, os.path.dirname, lambda x: x)

@pytest.fixture(autouse=True)
def path_exists_mock(monkeypatch: MonkeyPatch):
    return FunctionMock(monkeypatch, os.path.exists, True)

def test_handle_given_a_filter_import_should_import_the_filter_text(monkeypatch: MonkeyPatch, dirname_mock: FunctionMock):
    DIRECTORY = "directory"
    target_filter = create_filter("target filter contents", filepath="target_filter")
    filter = create_filter(f"{RULE_START}{IMPORT} {target_filter.filepath}", filepath="import_filter")
    filter_load_mock = FunctionMock(monkeypatch, Filter.load, target_filter, Filter)
    dirname_mock.result = DIRECTORY

    lines = import_.handle(filter, filter.blocks[0], None)

    assert filter_load_mock.received(f"{DIRECTORY}/{target_filter.filepath}{_FILTER_EXTENSION}")
    assert lines[-1] == str(target_filter.blocks[0].lines[0])

@pytest.mark.parametrize("import_description", [
    f"{_SPLITTER} {_TARGET_BLOCK_NAME} {_SPLITTER} {_TARGET_BLOCK_CONTENTS}",
    f"{_SPLITTER} {_TARGET_BLOCK_NAME}"
])
def test_handle_given_a_blockname_or_rule_pattern_should_import_the_appropriate_text(
    monkeypatch: MonkeyPatch, import_description: str):
    
    filter = create_filter(
    f"""{Operand.SHOW} {RULE_START}{_BLOCK_NAME} {_TARGET_BLOCK_NAME}
            {_TARGET_BLOCK_CONTENTS}
        {Operand.SHOW} {RULE_START}{IMPORT} {import_description}""")
    _ = FunctionMock(monkeypatch, Filter.load, filter, Filter)
    
    lines = import_.handle(filter, filter.blocks[1], None)

    assert lines[-1].lstrip() == _TARGET_BLOCK_CONTENTS

def test_handle_given_import_file_doesnt_exist_should_raise(path_exists_mock: FunctionMock):
    UNEXISTENT_FILEPATH = f"unexistent filepath"
    filter = create_filter(f"{RULE_START}{IMPORT} {UNEXISTENT_FILEPATH}")
    path_exists_mock.result = False

    with pytest.raises(ExpectedError) as error:
        import_.handle(filter, filter.blocks[0], None)

    assert path_exists_mock.received(f"{filter.filepath}/{UNEXISTENT_FILEPATH}{_FILTER_EXTENSION}")
    assert error.value.message == _FILTER_DOES_NOT_EXIST_ERROR.format(UNEXISTENT_FILEPATH)
    assert error.value.line_number == filter.blocks[0].lines[0].number
    assert error.value.filepath == filter.filepath

def test_handle_given_blockname_doesnt_exist_should_raise(monkeypatch: MonkeyPatch):
    UNEXISTENT_BLOCKNAME = "unexistent_blockname"
    filter = create_filter(f"{RULE_START}{IMPORT} {_SPLITTER} {UNEXISTENT_BLOCKNAME}")
    _ = FunctionMock(monkeypatch, Filter.load, filter, Filter)

    with pytest.raises(ExpectedError) as error:
        import_.handle(filter, filter.blocks[0], None)
    
    assert error.value.message == _BLOCK_NOT_FOUND_ERROR.format(UNEXISTENT_BLOCKNAME)
    assert error.value.filepath == filter.filepath

def test_handle_given_line_pattern_doesnt_exist_should_raise(monkeypatch: MonkeyPatch):
    UNEXISTENT_LINE_PATTERN = "unexistent line pattern"
    filter = create_filter(
    f"""{Operand.SHOW} {RULE_START}{_BLOCK_NAME} {_TARGET_BLOCK_NAME}
        {Operand.SHOW} {RULE_START}{IMPORT} {_SPLITTER} {_TARGET_BLOCK_NAME} {_SPLITTER} {UNEXISTENT_LINE_PATTERN}""")
    _ = FunctionMock(monkeypatch, Filter.load, filter, Filter)

    with pytest.raises(ExpectedError) as error:
        import_.handle(filter, filter.blocks[1], None)
    
    assert error.value.message == _LINE_PATTERN_NOT_FOUND_ERROR.format(UNEXISTENT_LINE_PATTERN, _TARGET_BLOCK_NAME)
    assert error.value.line_number == filter.blocks[0].line_number
    assert error.value.filepath == filter.filepath

def test_handle_given_incorrect_formatting_should_raise():
    RULE_DESCRPTION = f"1 {_SPLITTER} 2 {_SPLITTER} 3 {_SPLITTER} 4"
    filter = create_filter(f"{RULE_START}{IMPORT} {RULE_DESCRPTION}")

    with pytest.raises(ExpectedError) as error:
        import_.handle(filter, filter.blocks[0], None)

    assert error.value.message == _INCORRECT_RULE_FORMAT_ERROR.format(RULE_DESCRPTION)
    assert error.value.line_number == filter.blocks[0].lines[0].number
    assert error.value.filepath == filter.filepath

@pytest.mark.parametrize("rule_description, error_param", [
    (_SPLITTER, _BLOCK_NAME_ERROR_TEXT),
    (f"{_SPLITTER} block_name {_SPLITTER}", _LINE_PATTERN_ERROR_TEXT)
])
def test_handle_given_an_empty_parameter_should_raise(rule_description: str, error_param: str):
    filter = create_filter(f"{RULE_START}{IMPORT} {rule_description}")

    with pytest.raises(ExpectedError) as error:
        import_.handle(filter, filter.blocks[0], None)

    assert error.value.message == _EMPTY_PARAMETER_ERROR.format(rule_description, error_param)
    assert error.value.line_number == filter.blocks[0].lines[0].number
    assert error.value.filepath == filter.filepath

def test_handle_given_a_circular_reference_should_raise():
    BLOCK_NAME = "1"
    IMPORT_DESCRIPTION = f"{_SPLITTER} {BLOCK_NAME}"
    filter = create_filter(
    f"""{Operand.SHOW}  {RULE_START}{_BLOCK_NAME} {BLOCK_NAME}
        {RULE_START}{IMPORT} {IMPORT_DESCRIPTION}""")
    
    with pytest.raises(ExpectedError) as error:
        import_.handle(filter, filter.blocks[0], None)
    
    assert _CIRCULAR_REFERENCE_ERROR.format(IMPORT_DESCRIPTION, "") in error.value.message
    assert f"{filter.filepath} {IMPORT_DESCRIPTION}{_LOOP_STARTS_HERE_ERROR_TEXT}" in error.value.message
    assert f"{filter.filepath} {IMPORT_DESCRIPTION}{_LOOP_REPEATS_HERE_ERROR_TEXT}" in error.value.message
    assert error.value.line_number == filter.blocks[0].lines[1].number
    assert error.value.filepath == filter.filepath