import pytest, console
from pytest import MonkeyPatch
from console import functions
from core import ExpectedError
from test_utilities import FunctionMock
from rich.markdown import Markdown
from rich.console import Console
from console.functions import _DONE_MESSAGE, _EXPECTED_ERROR_TEMPLATE, _UNKNOWN_ERROR_MESSAGE

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

def test_err_given_an_expected_error_should_use_the_expected_error_template(console_print_mock: FunctionMock):
    ERROR = ExpectedError("an error", line_number=1, filepath="filepath")

    console.err(ERROR)

    assert console_print_mock.received(_EXPECTED_ERROR_TEMPLATE.format(ERROR))

def test_err_given_an_exception_should_write_the_unknown_error_message(
    console_print_mock: FunctionMock, console_print_exception_mock: FunctionMock):

    ERROR = Exception("a random exception")

    console.err(ERROR)

    assert console_print_mock.received(_UNKNOWN_ERROR_MESSAGE)
    assert console_print_exception_mock.received(show_locals=True)