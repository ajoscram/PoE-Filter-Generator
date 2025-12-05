import pytest
from commands import generate
from commands.generate import _HANDLER_NOT_FOUND_ERROR, _HANDLER_NOT_PROVIDED_ERROR, _TOO_LITTLE_ARGUMENTS_ERROR
from core import Delimiter, ExpectedError, Filter, Block
from handlers.context import Context
from handlers import Handler
from pytest import MonkeyPatch
from test_utilities import create_filter, FunctionMock

class _MockHandler(Handler):
    def __init__(self):
        super().__init__(self._handle_function, Context)
        self.name = "handler_name"
        self.options_handled = None
        self.filter_handled = None
        self.block_handled = None
    
    def _handle_function(self, block: Block, context: Context):
        self.options_handled = context.options
        self.filter_handled = context.filter
        self.block_handled = block
        return [ "line 1", "line 2" ]

@pytest.fixture(autouse=True)
def filter(monkeypatch: MonkeyPatch):
    filter = create_filter("filter text")
    _ = FunctionMock(monkeypatch, Filter.load, filter, target=Filter)
    return filter

@pytest.fixture()
def mock_handler(monkeypatch: MonkeyPatch):    
    # performing this setattr is fine because it is an import from another module
    mock_handler = _MockHandler()
    monkeypatch.setattr(generate, 'HANDLERS', { mock_handler.name: mock_handler })
    return mock_handler

def test_execute_given_a_handler_name_should_apply_it_and_save_the_new_filter(
    monkeypatch: MonkeyPatch, filter: Filter, mock_handler: _MockHandler):
    
    OPTIONS = [ "handler_option_1", "handler_option_2" ]
    ARGS = [ filter.filepath, Delimiter.HANDLER_START + mock_handler.name ] + OPTIONS
    save_filter_mock = FunctionMock(monkeypatch, Filter.save, target=Filter)

    generate.execute(ARGS)
    
    assert mock_handler.filter_handled == filter
    assert mock_handler.block_handled == filter.blocks[0]
    assert mock_handler.options_handled == OPTIONS
    assert save_filter_mock.get_invocation_count() == 1

def test_execute_given_less_than_2_args_should_raise():
    ARGS = [ "one" ]

    with pytest.raises(ExpectedError) as error:
        generate.execute(ARGS)

    assert error.value.message == _TOO_LITTLE_ARGUMENTS_ERROR

def test_execute_given_no_handler_was_passed_should_raise():
    ARGS = [ "no", "handler" ]

    with pytest.raises(ExpectedError) as error:
        generate.execute(ARGS)
    
    assert error.value.message == _HANDLER_NOT_PROVIDED_ERROR

def test_execute_given_an_unknown_handler_name_should_raise(filter: Filter):
    HANDLER_NAME = "unknown_handler"
    ARGS = [ filter.filepath, f"{Delimiter.HANDLER_START}{HANDLER_NAME}" ]

    with pytest.raises(ExpectedError) as error:
        generate.execute(ARGS)
    
    assert error.value.message == _HANDLER_NOT_FOUND_ERROR.format(HANDLER_NAME)