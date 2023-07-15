import pytest, os, subprocess
from commands import path
from commands.path import _COMMAND_EXECUTION_ERROR, _GENERIC_POWERSHELL_SCRIPT, _GET_PATH_SCRIPT, _NOT_ON_WINDOWS_ERROR, _POWERSHELL_NOT_FOUND_ERROR, _SET_PATH_SCRIPT, _WINDOWS_OS_NAME
from core import ExpectedError
from pytest import MonkeyPatch
from test_utilities import FunctionMock

_PATHSEP = ";"
_CURRENT_DIRECTORY = "current_directory"
_ENV_PATHS = "directory_1;directory_2"

class _CompletedProcessMock:
    def __init__(self, returncode: int = 0, stderr: str = "stderr", stdout: str = _ENV_PATHS):
        self.returncode = returncode
        self.stderr = stderr
        self.stdout = stdout

@pytest.fixture(autouse=True)
def os_props(monkeypatch: MonkeyPatch):
    monkeypatch.setattr(os, "name", _WINDOWS_OS_NAME)
    monkeypatch.setattr(os, "pathsep", _PATHSEP)

@pytest.fixture(autouse=True)
def os_getcwd_mock(monkeypatch: MonkeyPatch):
    return FunctionMock(monkeypatch, os.getcwd, _CURRENT_DIRECTORY)

@pytest.fixture(autouse=True)
def subprocess_run_mock(monkeypatch: MonkeyPatch):
    return FunctionMock(monkeypatch, subprocess.run, _CompletedProcessMock())

def test_execute_given_current_directory_is_new_should_append_it_to_env_path(
    subprocess_run_mock: FunctionMock):
    
    NEW_PATH = _ENV_PATHS + _PATHSEP + _CURRENT_DIRECTORY
    SET_PATH_COMMAND = _GENERIC_POWERSHELL_SCRIPT.format(_SET_PATH_SCRIPT.format(NEW_PATH))

    path.execute(None)

    assert subprocess_run_mock.received(SET_PATH_COMMAND)

def test_execute_given_current_directory_was_already_in_path_should_not_set_env_path(
    subprocess_run_mock: FunctionMock):
    
    ENV_PATHS = _ENV_PATHS + _PATHSEP + _CURRENT_DIRECTORY
    completed_process_mock = _CompletedProcessMock(stdout=ENV_PATHS)
    subprocess_run_mock.result = completed_process_mock

    path.execute(None)

    assert subprocess_run_mock.get_invocation_count() == 1 # invoked only once to get the path

def test_execute_given_not_on_windows_should_raise(monkeypatch: MonkeyPatch):
    monkeypatch.setattr(os, "name", "not windows")

    with pytest.raises(ExpectedError) as error:
        path.execute(None)

    assert error.value.message == _NOT_ON_WINDOWS_ERROR

def test_execute_given_powershell_is_not_found_should_raise(subprocess_run_mock: FunctionMock):
    subprocess_run_mock.result = FileNotFoundError()

    with pytest.raises(ExpectedError) as error:
        path.execute(None)
    
    assert error.value.message == _POWERSHELL_NOT_FOUND_ERROR

def test_execute_given_a_script_failed_should_raise(subprocess_run_mock: FunctionMock):
    completed_process_mock = _CompletedProcessMock(returncode=1) # non-zero return code means error
    subprocess_run_mock.result = completed_process_mock

    with pytest.raises(RuntimeError) as error:
        path.execute(None)

    assert str(error.value) == _COMMAND_EXECUTION_ERROR.format(
        _GENERIC_POWERSHELL_SCRIPT.format(_GET_PATH_SCRIPT),
        completed_process_mock.returncode,
        completed_process_mock.stderr,
        completed_process_mock.stdout)