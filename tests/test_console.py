import pytest, console, traceback
from pytest import MonkeyPatch
from console import functions
from core import ExpectedError, Delimiter
from test_utilities import FunctionMock
from rich.markdown import Markdown
from rich.console import Console
from console.functions import _COMMANDS_FOLDER_NAME, _DONE_MESSAGE, _EXPECTED_ERROR_TEMPLATE, _HANDLERS_FOLDER_NAME, _HINT_MESSAGE, _UNKNOWN_ERROR_MESSAGE, _DEFAULT_HINT_TERM, _WIKI_PAGE_URL

class _MockTrace:
    def __init__(self, filename: str):
        self.filename = filename

_ERROR = ExpectedError("an error", line_number=1, filepath="filepath")

@pytest.fixture()
def console_print_mock(monkeypatch: MonkeyPatch):
    return FunctionMock(monkeypatch, Console.print, target=functions._CONSOLE)

@pytest.fixture()
def console_print_exception_mock(monkeypatch: MonkeyPatch):
    return FunctionMock(monkeypatch, Console.print_exception, target=functions._CONSOLE)

def test_write_should_print_values_via_the_console(console_print_mock: FunctionMock):
    VALUES = ("first", "second", "third")

    console.write(*VALUES)

    assert console_print_mock.received(*VALUES)

def test_write_given_markdown_should_pass_a_markdown_to_the_console(console_print_mock: FunctionMock):
    TEXT = "# a markdown header"

    console.write(TEXT, markdown=True)

    markdown: Markdown = console_print_mock.get_arg(Markdown)
    assert markdown.markup == TEXT

def test_write_given_done_should_prepend_the_done_value(console_print_mock: FunctionMock):
    console.write(done=True)

    assert console_print_mock.received(_DONE_MESSAGE)

def test_err_given_an_exception_should_write_the_unknown_error_message(
    console_print_mock: FunctionMock, console_print_exception_mock: FunctionMock):

    ERROR = Exception("a random exception")

    console.err(ERROR)

    assert console_print_mock.received(_UNKNOWN_ERROR_MESSAGE)
    assert console_print_exception_mock.received(show_locals=True)

def test_err_given_an_expected_error_should_use_the_expected_error_template_and_default_hint(
    console_print_mock: FunctionMock):
    
    console.err(_ERROR)

    assert console_print_mock.received(_EXPECTED_ERROR_TEMPLATE.format(_ERROR))
    assert console_print_mock.received( \
        _HINT_MESSAGE.format(_DEFAULT_HINT_TERM, _WIKI_PAGE_URL.format(_DEFAULT_HINT_TERM)))

@pytest.mark.parametrize("folder, term_prefix", [
    (_HANDLERS_FOLDER_NAME, Delimiter.HANDLER_START),
    (_COMMANDS_FOLDER_NAME, Delimiter.COMMAND_START) ])
def test_err_given_an_expected_error_in_a_with_a_known_module_should_use_that_term_in_the_hint(
    folder: str, term_prefix: str, monkeypatch: MonkeyPatch, console_print_mock: FunctionMock):
    
    TERM_NAME = "term"
    _setup_traceback(monkeypatch, folder, TERM_NAME)

    console.err(_ERROR)

    term = term_prefix + TERM_NAME
    assert console_print_mock.received(_HINT_MESSAGE.format(term, _WIKI_PAGE_URL.format(term)))

def _setup_traceback(monkeypatch: MonkeyPatch, folder: str, filename: str):
    filepaths = [ "src\\main.py", f"src\\{folder}\\{filename}.py" ]
    mock_traces = [ _MockTrace(filepath) for filepath in reversed(filepaths) ]
    _ = FunctionMock(monkeypatch, traceback.extract_tb, mock_traces)