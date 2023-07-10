import sys, main, traceback, pytest, commands
from pytest import MonkeyPatch
from test_utilities import FunctionMock
from core import GeneratorError
from commands import help, COMMAND_NAME_PREFIX
from main import _COMMAND_NOT_FOUND_ERROR, _EXCEPTION_TEMPLATE, _GENERATOR_ERROR_TEMPLATE, _NO_ARGS_ERROR, _UNKNOWN_ERROR_MESSAGE

class _CommandMock:
    def __init__(self, name: str):
        self.name = name
        self.args_received = None
        self.exception: Exception = None
    
    def execute(self, args: list[str]):
        self.args_received = args
        if self.exception != None:
            raise self.exception
    
@pytest.fixture()
def command_mock(monkeypatch: MonkeyPatch):
    return _mock_COMMANDS_and_get_mock(monkeypatch, "command_name")

@pytest.fixture()
def help_mock(monkeypatch: MonkeyPatch):
    return FunctionMock(monkeypatch, help.execute, target=help)

@pytest.fixture()
def print_mock(monkeypatch: MonkeyPatch):
    return FunctionMock(monkeypatch, print)

def test_main_given_a_command_name_should_execute_the_command(monkeypatch: MonkeyPatch, command_mock: _CommandMock):
    ARGS = [ "some", "args" ]
    _mock_argv(monkeypatch, ARGS, command_mock)

    main.main()

    assert command_mock.args_received == ARGS

def test_main_given_no_command_name_should_use_default_instead(monkeypatch: MonkeyPatch):
    ARGS = [ "some", "args" ]
    command_mock = _mock_COMMANDS_and_get_mock(monkeypatch, commands.DEFAULT_COMMAND_NAME)
    _mock_argv(monkeypatch, ARGS)

    main.main()

    assert command_mock.args_received == ARGS

def test_main_given_unknown_command_should_handle_the_error(
    monkeypatch: MonkeyPatch, help_mock: FunctionMock, print_mock: FunctionMock):
    
    UNKNOWN_COMMAND = f"{COMMAND_NAME_PREFIX}unknown_command"
    _mock_argv(monkeypatch, [ UNKNOWN_COMMAND ])

    main.main()

    assert print_mock.received(_GENERATOR_ERROR_TEMPLATE.format(
        GeneratorError(_COMMAND_NOT_FOUND_ERROR.format(UNKNOWN_COMMAND))))
    assert help_mock.get_invocation_count() == 1

def test_main_given_no_args_were_passed_should_handle_the_error(
    monkeypatch: MonkeyPatch, help_mock: FunctionMock, print_mock: FunctionMock):

    _mock_argv(monkeypatch, [])

    main.main()

    assert print_mock.received(_GENERATOR_ERROR_TEMPLATE.format(GeneratorError(_NO_ARGS_ERROR)))
    assert help_mock.get_invocation_count() == 1

def test_main_given_an_exception_is_raised_should_handle_it(
    monkeypatch: MonkeyPatch, command_mock: _CommandMock, print_mock: FunctionMock):
    
    command_mock.exception = Exception("message")
    traceback_mock = FunctionMock(monkeypatch, traceback.print_tb)
    _mock_argv(monkeypatch, command_mock=command_mock)

    main.main()

    assert print_mock.received(_UNKNOWN_ERROR_MESSAGE)
    assert traceback_mock.received(command_mock.exception.__traceback__)
    assert print_mock.received(_EXCEPTION_TEMPLATE.format(
        type(command_mock.exception).__name__, command_mock.exception))

def _mock_argv(monkeypatch: MonkeyPatch, args: list[str] = [], command_mock: _CommandMock = None):
    if command_mock != None:
        args = [ COMMAND_NAME_PREFIX + command_mock.name ] + args
    args = [ "program.py" ] + args
    monkeypatch.setattr(sys, 'argv', args)

def _mock_COMMANDS_and_get_mock(monkeypatch: MonkeyPatch, command_name: str):
    command_mock = _CommandMock(command_name)
    mock_commands_dict = { command_mock.name: command_mock.execute }
    monkeypatch.setattr(commands, "COMMANDS", mock_commands_dict)
    return command_mock