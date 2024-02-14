import sys, main, pytest, console
from pytest import MonkeyPatch
from test_utilities import FunctionMock
from core import ExpectedError, COMMAND_START, ERROR_EXIT_CODE
from commands import DEFAULT_COMMAND_NAME
from main import _COMMAND_NOT_FOUND_ERROR, _NO_ARGS_ERROR

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
def console_err_mock(monkeypatch: MonkeyPatch):
    return FunctionMock(monkeypatch, console.err)

@pytest.fixture()
def sys_exit_mock(monkeypatch: MonkeyPatch):
    return FunctionMock(monkeypatch, sys.exit)

def test_main_given_a_command_name_should_execute_the_command(
    monkeypatch: MonkeyPatch, command_mock: _CommandMock):
    
    ARGS = [ "some", "args" ]
    _mock_argv(monkeypatch, ARGS, command_mock)

    main.main()

    assert command_mock.args_received == ARGS

def test_main_given_no_command_name_should_use_default_instead(monkeypatch: MonkeyPatch):
    ARGS = [ "some", "args" ]
    command_mock = _mock_COMMANDS_and_get_mock(monkeypatch, DEFAULT_COMMAND_NAME)
    _mock_argv(monkeypatch, ARGS)

    main.main()

    assert command_mock.args_received == ARGS

def test_main_given_unknown_command_should_print_error_and_exit(
    monkeypatch: MonkeyPatch, console_err_mock: FunctionMock, sys_exit_mock: FunctionMock):
    
    UNKNOWN_COMMAND = f"{COMMAND_START}unknown_command"
    _mock_argv(monkeypatch, [ UNKNOWN_COMMAND ])

    main.main()

    error_received: ExpectedError = console_err_mock.get_arg(ExpectedError)
    assert error_received.message == _COMMAND_NOT_FOUND_ERROR.format(UNKNOWN_COMMAND)
    assert sys_exit_mock.received(ERROR_EXIT_CODE)

def test_main_given_no_args_were_passed_should_print_error_and_exit(
    monkeypatch: MonkeyPatch, console_err_mock: FunctionMock, sys_exit_mock: FunctionMock):

    _mock_argv(monkeypatch, [])

    main.main()

    error_received: ExpectedError = console_err_mock.get_arg(ExpectedError)
    assert error_received.message == _NO_ARGS_ERROR
    assert sys_exit_mock.received(ERROR_EXIT_CODE)

def test_main_given_an_exception_is_raised_should_print_error_and_exit(
    monkeypatch: MonkeyPatch, command_mock: _CommandMock, console_err_mock: FunctionMock, sys_exit_mock: FunctionMock):
    
    command_mock.exception = Exception("message")
    _mock_argv(monkeypatch, command_mock=command_mock)

    main.main()

    exception_received: Exception = console_err_mock.get_arg(Exception)
    assert exception_received == command_mock.exception
    assert sys_exit_mock.received(ERROR_EXIT_CODE)

def _mock_argv(monkeypatch: MonkeyPatch, args: list[str] = [], command_mock: _CommandMock = None):
    if command_mock != None:
        args = [ COMMAND_START + command_mock.name ] + args
    args = [ "program.py" ] + args
    monkeypatch.setattr(sys, 'argv', args)

def _mock_COMMANDS_and_get_mock(monkeypatch: MonkeyPatch, command_name: str):
    command_mock = _CommandMock(command_name)
    mock_commands_dict = { command_mock.name: command_mock.execute }

    # performing this setattr is fine because it is an import from another module
    monkeypatch.setattr(main, "COMMANDS", mock_commands_dict)
    
    return command_mock