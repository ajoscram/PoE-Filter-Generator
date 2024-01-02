import pytest, os, subprocess, utils
from commands import path
from commands.path import _ARGS_ERROR, _COMMAND_EXECUTION_ERROR, _GENERIC_POWERSHELL_SCRIPT, _GET_PATH_SCRIPT, _NOT_ON_WINDOWS_ERROR, _POWERSHELL_NOT_FOUND_ERROR, _REMOVE_ARG, _SET_PATH_SCRIPT, _WINDOWS_OS_NAME
from core import ExpectedError
from pytest import MonkeyPatch
from test_utilities import FunctionMock

_PATHSEP = ";"
_EXE_DIR = "exe_dir"
_EXISTING_DIR_1 = "directory_1"
_EXISTING_DIR_2 = "directory_2"
_ENV_PATHS = _EXISTING_DIR_1 + _PATHSEP + _EXISTING_DIR_2

class _CompletedProcessMock:
    def __init__(self, returncode: int = 0, stderr: str = "stderr", stdout: str = _ENV_PATHS):
        self.returncode = returncode
        self.stderr = stderr
        self.stdout = stdout

@pytest.fixture(autouse=True)
def get_execution_dir_mock(monkeypatch: MonkeyPatch):
    return FunctionMock(monkeypatch, utils.get_execution_dir, _EXE_DIR)

@pytest.fixture(autouse=True)
def setup(monkeypatch: MonkeyPatch):
    monkeypatch.setattr(os, "name", _WINDOWS_OS_NAME)
    monkeypatch.setattr(os, "pathsep", _PATHSEP)
    _ = FunctionMock(monkeypatch, os.path.abspath, lambda x: x)

@pytest.fixture(autouse=True)
def subprocess_run_mock(monkeypatch: MonkeyPatch):
    return FunctionMock(monkeypatch, subprocess.run, _CompletedProcessMock())

def test_execute_given_current_directory_is_new_should_append_it_to_env_path(
    subprocess_run_mock: FunctionMock):
    
    NEW_PATH = _ENV_PATHS + _PATHSEP + _EXE_DIR
    SET_PATH_COMMAND = _GENERIC_POWERSHELL_SCRIPT.format(_SET_PATH_SCRIPT.format(NEW_PATH))

    path.execute([])

    assert subprocess_run_mock.received(SET_PATH_COMMAND)

def test_execute_given_remove_and_current_directory_is_found_on_path_should_remove_it(
    monkeypatch: MonkeyPatch, subprocess_run_mock: FunctionMock, get_execution_dir_mock: FunctionMock):
    
    _ = FunctionMock(monkeypatch, os.path.samefile, lambda x, y: x == y)
    SET_PATH_COMMAND = _GENERIC_POWERSHELL_SCRIPT.format(_SET_PATH_SCRIPT.format(_EXISTING_DIR_1))
    get_execution_dir_mock.result = _EXISTING_DIR_2

    path.execute([ _REMOVE_ARG ])

    assert subprocess_run_mock.received(SET_PATH_COMMAND)

def test_execute_given_current_directory_was_already_in_path_should_not_set_env_path(
    subprocess_run_mock: FunctionMock):
    
    ENV_PATHS = _ENV_PATHS + _PATHSEP + _EXE_DIR
    completed_process_mock = _CompletedProcessMock(stdout=ENV_PATHS)
    subprocess_run_mock.result = completed_process_mock

    path.execute([])

    assert subprocess_run_mock.get_invocation_count() == 1 # invoked only once to get the path

def test_execute_given_remove_and_current_directory_was_not_in_path_should_not_remove(
    subprocess_run_mock: FunctionMock):
    
    completed_process_mock = _CompletedProcessMock(stdout=_ENV_PATHS)
    subprocess_run_mock.result = completed_process_mock

    path.execute([ _REMOVE_ARG ])

    assert subprocess_run_mock.get_invocation_count() == 1 # invoked only once to get the path

def test_execute_given_not_on_windows_should_raise(monkeypatch: MonkeyPatch):
    monkeypatch.setattr(os, "name", "not windows")

    with pytest.raises(ExpectedError) as error:
        path.execute([])

    assert error.value.message == _NOT_ON_WINDOWS_ERROR

def test_execute_given_powershell_is_not_found_should_raise(subprocess_run_mock: FunctionMock):
    subprocess_run_mock.result = FileNotFoundError()

    with pytest.raises(ExpectedError) as error:
        path.execute([])
    
    assert error.value.message == _POWERSHELL_NOT_FOUND_ERROR

def test_execute_given_a_script_failed_should_raise(subprocess_run_mock: FunctionMock):
    completed_process_mock = _CompletedProcessMock(returncode=1) # non-zero return code means error
    subprocess_run_mock.result = completed_process_mock

    with pytest.raises(ExpectedError) as error:
        path.execute([])

    assert error.value.message == _COMMAND_EXECUTION_ERROR.format(
        _GENERIC_POWERSHELL_SCRIPT.format(_GET_PATH_SCRIPT),
        completed_process_mock.returncode,
        completed_process_mock.stderr,
        completed_process_mock.stdout)

@pytest.mark.parametrize("args", [ [ "more_than", "one_arg" ], [ "not_remove" ] ])
def test_execute_given_incorrect_args_should_raise(args: list[str]):
    with pytest.raises(ExpectedError) as error:
        path.execute(args)

    assert error.value.message == _ARGS_ERROR.format(" ".join(args))