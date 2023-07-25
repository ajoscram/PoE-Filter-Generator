import pytest, console, web
from core import ExpectedError
from pytest import MonkeyPatch
from test_utilities import FunctionMock
from commands import help
from commands.help import _API_URL, _TOO_MANY_ARGS_ERROR, DEFAULT_WIKI_PAGE_NAME

@pytest.fixture(autouse=True)
def console_write_mock(monkeypatch: MonkeyPatch):
    return FunctionMock(monkeypatch, console.write)

@pytest.fixture(autouse=True)
def web_get_mock(monkeypatch: MonkeyPatch):
    WIKI_TEXT = "Text returned by doing a request from the Wiki."
    return FunctionMock(monkeypatch, web.get, WIKI_TEXT)

def test_execute_given_a_term_should_write_as_markdown(
    console_write_mock: FunctionMock, web_get_mock: FunctionMock):
    
    TERM = "Term"

    help.execute(None, [ TERM ])

    text_written = console_write_mock.get_arg(str)
    assert TERM in text_written
    assert web_get_mock.result in text_written
    assert web_get_mock.received(_API_URL.format(TERM), json=False)
    assert console_write_mock.received(markdown=True)

def test_execute_given_no_parameters_should_default_to_the_usage_page(web_get_mock: FunctionMock):
    help.execute(None, [])

    assert web_get_mock.received(_API_URL.format(DEFAULT_WIKI_PAGE_NAME))

def test_execute_given_more_than_1_argument_should_raise():
    TERMS = [ "1", "2" ]

    with pytest.raises(ExpectedError) as error:
        help.execute(None, TERMS)

    assert error.value.message == _TOO_MANY_ARGS_ERROR.format(len(TERMS))