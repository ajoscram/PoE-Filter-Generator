import os, pytest
from pytest import MonkeyPatch
from core import ExpectedError, Filter, Operand, Delimiter
from handlers import import_
from handlers.import_ import _BLOCKNAME_SEGMENT, _EMPTY_SEGMENT_ERROR, _NAVIGATION_SEGMENT, _SEGMENT_ERROR_PRELUDE, _SEGMENT_FORMAT_ERROR, _TEMPLATE_SEGMENT, ImportContext, _Navigation, _Splitter, NAME as IMPORT, _ROOT_NOT_FOUND_ERROR, _NAME_RULE, _BLOCK_NOT_FOUND_ERROR, _CIRCULAR_REFERENCE_ERROR, _FILTER_DOES_NOT_EXIST_ERROR, _FILTER_EXTENSION, _LOOP_REPEATS_HERE_ERROR_TEXT, _LOOP_STARTS_HERE_ERROR_TEXT
from test_utilities import create_filter, FunctionMock

_TARGET_BLOCK_NAME = "block_name"
_TARGET_BLOCK_CONTENTS = "block contents here"

@pytest.fixture(autouse=True)
def setup(monkeypatch: MonkeyPatch):
    _ = FunctionMock(monkeypatch, os.path.normpath, lambda x: x)
    _ = FunctionMock(monkeypatch, os.path.samefile, lambda x, y: x == y)
    _ = FunctionMock(monkeypatch, os.path.abspath, lambda x: x)

@pytest.fixture(autouse=True)
def dirname_mock(monkeypatch: MonkeyPatch):
    return FunctionMock(monkeypatch, os.path.dirname, lambda x: x)

@pytest.fixture(autouse=True)
def path_isfile_mock(monkeypatch: MonkeyPatch):
    return FunctionMock(monkeypatch, os.path.isfile, True)

def test_handle_given_a_filter_import_should_import_the_filter_text(monkeypatch: MonkeyPatch, dirname_mock: FunctionMock):
    DIRECTORY = "directory"
    target_filter = create_filter("target filter contents", filepath="target_filter")
    filter = create_filter(f"{Delimiter.RULE_START}{IMPORT} {target_filter.filepath}", filepath="import_filter")
    filter_load_mock = FunctionMock(monkeypatch, Filter.load, target_filter, Filter)
    dirname_mock.result = DIRECTORY

    lines = import_.handle(filter.blocks[0], ImportContext(filter, []))

    assert filter_load_mock.received(f"{DIRECTORY}/{target_filter.filepath}{_FILTER_EXTENSION}")
    assert lines[-1] == str(target_filter.blocks[0].lines[0])

def test_handle_given_a_blockname_should_import_the_appropriate_text(monkeypatch: MonkeyPatch):
    IMPORT_DESCRIPTION = f"{_Splitter.BLOCKNAME} {_TARGET_BLOCK_NAME}"
    filter = create_filter(
    f"""{Operand.SHOW} {Delimiter.RULE_START}{_NAME_RULE} {_TARGET_BLOCK_NAME}
            {_TARGET_BLOCK_CONTENTS}
        {Operand.SHOW} {Delimiter.RULE_START}{IMPORT} {IMPORT_DESCRIPTION}""")
    _ = FunctionMock(monkeypatch, Filter.load, filter, Filter)
    
    lines = import_.handle(filter.blocks[1], ImportContext(filter, []))

    assert lines[-1].lstrip() == _TARGET_BLOCK_CONTENTS

def test_handle_given_an_empty_root_should_resolve_to_the_filters_directory(
    monkeypatch: MonkeyPatch, dirname_mock: FunctionMock):

    target_filter = create_filter("target filter contents", filepath="target_filter")
    filter = create_filter(f"{Delimiter.RULE_START}{IMPORT} {_Splitter.ROOT} {target_filter.filepath}")
    filter_load_mock = FunctionMock(monkeypatch, Filter.load, target_filter, Filter)
    dirname_mock.result = "" # empty string means current filter's directory

    lines = import_.handle(filter.blocks[0], ImportContext(filter, []))

    assert filter_load_mock.received(f"{target_filter.filepath}{_FILTER_EXTENSION}")
    assert lines[-1] == str(target_filter.blocks[0].lines[0])

def test_handle_given_a_root_should_resolve_to_the_directory_passed_via_options(
    monkeypatch: MonkeyPatch, dirname_mock: FunctionMock):
    
    ROOT_NAME = "ROOT_DIR"
    ROOT_NAVIGATION = f"root"
    OPTIONS = [ ROOT_NAME, Delimiter.PAIR_SEPARATOR, ROOT_NAVIGATION ]
    target_filter = create_filter("target filter contents", filepath="target_filter")
    filter = create_filter(f"{Delimiter.RULE_START}{IMPORT} {ROOT_NAME} {_Splitter.ROOT} {target_filter.filepath}")
    filter_load_mock = FunctionMock(monkeypatch, Filter.load, target_filter, Filter)
    dirname_mock.result = "" # empty string means current filter's directory

    lines = import_.handle(filter.blocks[0], ImportContext(filter, OPTIONS))

    assert filter_load_mock.received(f"{ROOT_NAVIGATION}/{target_filter.filepath}{_FILTER_EXTENSION}")
    assert lines[-1] == str(target_filter.blocks[0].lines[0])

def test_handle_given_import_file_doesnt_exist_should_raise(path_isfile_mock: FunctionMock):
    UNEXISTENT_FILEPATH = "unexistent_filepath"
    filter = create_filter(f"{Delimiter.RULE_START}{IMPORT} {UNEXISTENT_FILEPATH}")
    path_isfile_mock.result = False

    with pytest.raises(ExpectedError) as error:
        import_.handle(filter.blocks[0], ImportContext(filter, []))

    assert path_isfile_mock.received(f"{filter.filepath}/{UNEXISTENT_FILEPATH}{_FILTER_EXTENSION}")
    assert error.value.message == _FILTER_DOES_NOT_EXIST_ERROR.format(UNEXISTENT_FILEPATH)
    assert error.value.line_number == filter.blocks[0].lines[0].number
    assert error.value.filepath == filter.filepath

def test_handle_given_blockname_doesnt_exist_should_raise(monkeypatch: MonkeyPatch):
    UNEXISTENT_BLOCKNAME = "unexistent_blockname"
    filter = create_filter(f"{Delimiter.RULE_START}{IMPORT} {_Splitter.BLOCKNAME} {UNEXISTENT_BLOCKNAME}")
    _ = FunctionMock(monkeypatch, Filter.load, filter, Filter)

    with pytest.raises(ExpectedError) as error:
        import_.handle(filter.blocks[0], ImportContext(filter, []))
    
    assert error.value.message == _BLOCK_NOT_FOUND_ERROR.format(UNEXISTENT_BLOCKNAME)
    assert error.value.filepath == filter.filepath

@pytest.mark.parametrize("rule_description, segment_splitter", [
    (f"navigation {_Splitter.BLOCKNAME}", _Splitter.BLOCKNAME),
    (f"navigation {_Splitter.TEMPLATE}", _Splitter.TEMPLATE),
])
def test_handle_given_an_empty_segment_that_shouldnt_should_raise(
    rule_description: str, segment_splitter: _Splitter):
    
    filter = create_filter(f"{Delimiter.RULE_START}{IMPORT} {rule_description}")

    with pytest.raises(ExpectedError) as error:
        import_.handle(filter.blocks[0], ImportContext(filter, []))

    assert error.value.message == _EMPTY_SEGMENT_ERROR.format(rule_description, segment_splitter.name.lower())
    assert error.value.line_number == filter.blocks[0].lines[0].number
    assert error.value.filepath == filter.filepath

def test_handle_given_a_circular_reference_should_raise():
    BLOCK_NAME = "block"
    IMPORT_DESCRIPTION = f"{_Splitter.BLOCKNAME} {BLOCK_NAME}"
    filter = create_filter(
    f"""{Operand.SHOW}  {Delimiter.RULE_START}{_NAME_RULE} {BLOCK_NAME}
        {Delimiter.RULE_START}{IMPORT} {IMPORT_DESCRIPTION}""")
    
    with pytest.raises(ExpectedError) as error:
        import_.handle(filter.blocks[0], ImportContext(filter, []))

    assert _CIRCULAR_REFERENCE_ERROR.format(IMPORT_DESCRIPTION, "") in error.value.message
    assert f"{filter.filepath} {IMPORT_DESCRIPTION}{_LOOP_STARTS_HERE_ERROR_TEXT}" in error.value.message
    assert f"{filter.filepath} {IMPORT_DESCRIPTION}{_LOOP_REPEATS_HERE_ERROR_TEXT}" in error.value.message
    assert error.value.line_number == filter.blocks[0].lines[1].number
    assert error.value.filepath == filter.filepath

def test_handle_given_root_in_import_not_specified_through_options_should_raise():
    MISSING_ROOT = f"missing_root"
    DESCRIPTION = f"{MISSING_ROOT} {_Splitter.ROOT} file"
    filter = create_filter(
        f"{Delimiter.RULE_START}{IMPORT} {DESCRIPTION}")

    with pytest.raises(ExpectedError) as error:
        import_.handle(filter.blocks[0], ImportContext(filter, []))
    
    assert error.value.message == _ROOT_NOT_FOUND_ERROR.format(MISSING_ROOT, DESCRIPTION)

@pytest.mark.parametrize("splitter, segment_name", [
    (_Splitter.ROOT, _NAVIGATION_SEGMENT.name),
    (_Splitter.BLOCKNAME, _BLOCKNAME_SEGMENT.name),
    (_Splitter.TEMPLATE, _TEMPLATE_SEGMENT.name) ])
def test_handle_given_too_many_splitters_in_import_should_raise(splitter: _Splitter, segment_name: str):
    ERROR_PORTION = f"many {splitter} splitters"
    MISFORMATTED_DESCRIPTION = f"too {splitter} " + ERROR_PORTION
    filter = create_filter(
        f"{Delimiter.RULE_START}{IMPORT} {MISFORMATTED_DESCRIPTION}")

    with pytest.raises(ExpectedError) as error:
        import_.handle(filter.blocks[0], ImportContext(filter, []))

    assert error.value.message == _SEGMENT_FORMAT_ERROR.format(
        MISFORMATTED_DESCRIPTION,
        segment_name,
        ERROR_PORTION,
        splitter.name.lower(),
        splitter)