from pytest import MonkeyPatch
from test_utilities import FunctionMock
from commands import help
from commands.help import _HELP_MESSAGE

def test_execute_should_print_the_help_message(monkeypatch: MonkeyPatch):
    print_mock = FunctionMock(monkeypatch, print)

    help.execute(None)

    assert print_mock.received(_HELP_MESSAGE)