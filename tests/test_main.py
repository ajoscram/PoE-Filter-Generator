import sys, main, pytest, traceback
from pytest import MonkeyPatch
from test_utilities import FunctionMock
from core import GeneratorError, Filter, Generator, Arguments
from core.constants import RULE_SEPARATOR
from main import _APPLYING_HANDLER_MESSAGE, _DONE_MESSAGE, _EXCEPTION_TEMPLATE, _GENERATOR_ERROR_TEMPLATE, _HELP_MESSAGE, _HELP_ARG, _HELP_ARG_SHORT, _READING_FILTER_MESSAGE, _SAVING_FILTER_MESSAGE, _UNKNOWN_ERROR_MESSAGE

@pytest.mark.parametrize('help_arg', [ _HELP_ARG, _HELP_ARG_SHORT ])
def test_main_given_a_help_parameter_was_passed_should_show_help(monkeypatch: MonkeyPatch, help_arg: str):
    monkeypatch.setattr(sys, 'argv', [ "filename", help_arg ])
    print_mock = FunctionMock(monkeypatch, print)
    exit_mock = FunctionMock(monkeypatch, sys.exit)

    main.main()

    assert print_mock.received(_HELP_MESSAGE)
    assert exit_mock.get_invocation_count() == 1

def test_main_given_normal_execution_should_succeed(monkeypatch: MonkeyPatch):
    INPUT_FILTER = Filter("in.filter", [])
    OUTPUT_FILTER = Filter("out.filter", [])
    HANDLER_NAME = "handler"
    HANDLER_OPTIONS = [ "option1", "option2" ]
    ARGS = [ "program_name.py", INPUT_FILTER.filepath, OUTPUT_FILTER.filepath, RULE_SEPARATOR + HANDLER_NAME ] + HANDLER_OPTIONS
    monkeypatch.setattr(sys, 'argv', ARGS)
    print_mock = FunctionMock(monkeypatch, print)
    save_filter_mock = FunctionMock(monkeypatch, Filter.save, target=Filter)
    load_filter_mock = FunctionMock(monkeypatch, Filter.load, INPUT_FILTER, Filter)
    generate_mock = FunctionMock(monkeypatch, Generator.generate, OUTPUT_FILTER, Generator)

    main.main()

    assert print_mock.received(_READING_FILTER_MESSAGE.format(INPUT_FILTER.filepath))
    assert load_filter_mock.received(INPUT_FILTER.filepath)
    assert print_mock.received(_APPLYING_HANDLER_MESSAGE.format(' '.join([HANDLER_NAME] + HANDLER_OPTIONS)))
    assert generate_mock.received(INPUT_FILTER, OUTPUT_FILTER.filepath, HANDLER_NAME, HANDLER_OPTIONS)
    assert print_mock.received(_SAVING_FILTER_MESSAGE.format(OUTPUT_FILTER.filepath))
    assert save_filter_mock.get_invocation_count() == 1
    assert print_mock.received(_DONE_MESSAGE)

def test_main_given_a_generator_error_is_raised_should_print_it(monkeypatch: MonkeyPatch):
    ERROR = GeneratorError("message", 1, "filepath")
    _ = FunctionMock(monkeypatch, Arguments.__init__, ERROR, Arguments)
    print_mock = FunctionMock(monkeypatch, print)

    main.main()

    assert print_mock.received(_GENERATOR_ERROR_TEMPLATE.format(ERROR, _HELP_MESSAGE))

def test_main_given_an_exception_is_raised_should_print_it(monkeypatch: MonkeyPatch):
    EXCEPTION = Exception("message")
    _ = FunctionMock(monkeypatch, Arguments.__init__, EXCEPTION, Arguments)
    print_mock = FunctionMock(monkeypatch, print)
    traceback_mock = FunctionMock(monkeypatch, traceback.print_tb)

    main.main()

    assert print_mock.received(_UNKNOWN_ERROR_MESSAGE)
    assert traceback_mock.received(EXCEPTION.__traceback__)
    assert print_mock.received(_EXCEPTION_TEMPLATE.format(type(EXCEPTION).__name__, EXCEPTION))