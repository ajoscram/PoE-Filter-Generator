import console
from pytest import MonkeyPatch
from test_utilities import FunctionMock
from commands import help
from commands.help import _HELP_MESSAGE

def test_execute_should_call_console_write_with_the_help_message(monkeypatch: MonkeyPatch):
    console_write_mock = FunctionMock(monkeypatch, console.write)

    help.execute(None, None)

    assert console_write_mock.received(_HELP_MESSAGE)