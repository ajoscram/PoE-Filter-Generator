import pytest, console, web
from pytest import MonkeyPatch
from test_utilities import FunctionMock
from commands import help
from commands.help import _API_URL, _SHORT, _USAGE_PAGE_NAME, _WEB_PAGE_URL

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

def test_execute_given_the_short_argument_should_print_the_short_version_instead(
    console_write_mock: FunctionMock):
    
    TERM = "Term"

    help.execute(None, [ TERM, _SHORT ])

    text_written = console_write_mock.get_arg(str)
    assert _WEB_PAGE_URL.format(TERM) in text_written
    assert console_write_mock.received(markdown=False)

def test_execute_given_no_parameters_should_default_to_the_usage_page(web_get_mock: FunctionMock):
    help.execute(None, [])

    assert web_get_mock.received(_API_URL.format(_USAGE_PAGE_NAME))