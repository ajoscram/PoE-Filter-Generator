import pytest, os, sys, watcher, console
from pytest import MonkeyPatch
from core import ExpectedError, ERROR_EXIT_CODE
from commands import watch, generate
from test_utilities import FunctionMock
from commands.watch import _GenerateCallable, _ARGUMENT_COUNT_ERROR, _INPUT_FILEPATH_ERROR, _OUTPUT_SUBDIRECTORY_OF_INPUT_ERROR, _FILTER_GLOB

def test_execute_given_valid_input_and_output_dirs_should_invoke_the_watcher(monkeypatch: MonkeyPatch):
    ROOT_DIR = "root"
    SUB_DIR = os.path.join(ROOT_DIR, "subdir")
    ARGS = [
        os.path.join(SUB_DIR, "input.filter"),
        os.path.join(ROOT_DIR, "output.filter"),
        ".handler" ]
    watcher_mock = FunctionMock(monkeypatch, watcher.watch)
    _ = FunctionMock(monkeypatch, os.path.abspath, lambda x: x)
    _ = FunctionMock(monkeypatch, os.path.isfile, True)

    watch.execute(ARGS)
    
    action = watcher_mock.get_arg(_GenerateCallable)
    assert action._args == ARGS
    assert watcher_mock.received(SUB_DIR, [ _FILTER_GLOB ])

def test_execute_given_too_little_arguments_should_raise():
    ARGS = [ "too little args" ]

    with pytest.raises(ExpectedError) as error:
        watch.execute(ARGS)
    
    assert error.value.message == _ARGUMENT_COUNT_ERROR

def test_execute_given_input_is_not_a_filepath_should_raise(monkeypatch: MonkeyPatch):
    ARGS = [ "not_a_valid_path", "output.filter", ".handler" ]
    _ = FunctionMock(monkeypatch, os.path.isfile, False)

    with pytest.raises(ExpectedError) as error:
        watch.execute(ARGS)
    
    assert error.value.message == _INPUT_FILEPATH_ERROR.format(ARGS[0])

def test_execute_given_output_dir_is_subdir_of_input_should_raise(monkeypatch: MonkeyPatch):
    ROOT_DIR = "root"
    SUB_DIR = os.path.join(ROOT_DIR, "subdir")
    ARGS = [
        os.path.join(ROOT_DIR, "input.filter"),
        os.path.join(SUB_DIR, "output.filter"),
        ".handler" ]
    _ = FunctionMock(monkeypatch, os.path.isfile, True)
    _ = FunctionMock(monkeypatch, os.path.abspath, lambda x: x)

    with pytest.raises(ExpectedError) as error:
        watch.execute(ARGS)
    
    assert error.value.message == _OUTPUT_SUBDIRECTORY_OF_INPUT_ERROR.format(ROOT_DIR, SUB_DIR)

def test_GenerateAction_given_invocation_should_execute_the_generator(monkeypatch: MonkeyPatch):
    ARGS = [ "arg", "another_arg" ]
    generate_mock = FunctionMock(monkeypatch, generate.execute, target=generate)

    action = _GenerateCallable(ARGS)
    action()

    assert generate_mock.get_invocation_count() == 1
    assert generate_mock.received(ARGS)

def test_GenerateAction_given_generator_raises_should_print_error_and_exit(monkeypatch: MonkeyPatch):
    ERROR = Exception("some exception")
    sys_exit_mock = FunctionMock(monkeypatch, sys.exit)
    console_err_mock = FunctionMock(monkeypatch, console.err)
    _ = FunctionMock(monkeypatch, generate.execute, ERROR, target=generate)

    action = _GenerateCallable([])
    action()

    assert console_err_mock.received(ERROR)
    assert sys_exit_mock.received(ERROR_EXIT_CODE)