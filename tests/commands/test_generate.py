import pytest, handlers
from commands import generate
from commands.generate import _HANDLER_NOT_FOUND_ERROR, _HANDLER_NOT_PROVIDED_ERROR, _TOO_LITTLE_ARGUMENTS_ERROR, _HANDLER_TAG
from core import GeneratorError, Filter, Block
from pytest import MonkeyPatch
from test_utilities import create_filter, FunctionMock

class _MockHandler:
    def __init__(self):
        self.name = "handler_name"
        self.lines = [ "line 1", "line 2" ]
        self.options_handled = None
        self.filter_handled = None
        self.block_handled = None
    
    def handle(self, filter: Filter, block: Block, options: list[str]):
        self.options_handled = options
        self.filter_handled = filter
        self.block_handled = block
        return self.lines

@pytest.fixture(autouse=True)
def filter(monkeypatch: MonkeyPatch):
    filter = create_filter(f"filter text")
    _ = FunctionMock(monkeypatch, Filter.load, filter, target=Filter)
    return filter

@pytest.fixture()
def mock_handler(monkeypatch: MonkeyPatch):
    mock_handler = _MockHandler()
    handlers_dict = { mock_handler.name: mock_handler.handle }
    monkeypatch.setattr(handlers, 'HANDLERS', handlers_dict)
    return mock_handler

def test_execute_given_a_handler_name_should_apply_it_and_save_the_new_filter(
    monkeypatch: MonkeyPatch, filter: Filter, mock_handler: _MockHandler):
    
    OPTIONS = [ "handler_option_1", "handler_option_2" ]
    ARGS = [ filter.filepath, _HANDLER_TAG + mock_handler.name ] + OPTIONS
    save_filter_mock = FunctionMock(monkeypatch, Filter.save, target=Filter)

    generate.execute(ARGS)
    
    assert mock_handler.filter_handled == filter
    assert mock_handler.block_handled == filter.blocks[0]
    assert mock_handler.options_handled == OPTIONS
    assert save_filter_mock.get_invocation_count() == 1

def test_execute_given_less_than_2_args_should_raise():
    ARGS = [ "one" ]

    with pytest.raises(GeneratorError) as error:
        generate.execute(ARGS)

    assert error.value.message == _TOO_LITTLE_ARGUMENTS_ERROR

def test_execute_given_no_handler_was_passed_should_raise():
    ARGS = [ "no", "handler" ]

    with pytest.raises(GeneratorError) as error:
        generate.execute(ARGS)
    
    assert error.value.message == _HANDLER_NOT_PROVIDED_ERROR

def test_execute_given_an_unknown_handler_name_should_raise(filter: Filter):
    HANDLER_NAME = "unknown_handler"
    ARGS = [ filter.filepath, f"{_HANDLER_TAG}{HANDLER_NAME}" ]

    with pytest.raises(GeneratorError) as error:
        generate.execute(ARGS)
    
    assert error.value.message == _HANDLER_NOT_FOUND_ERROR.format(HANDLER_NAME)