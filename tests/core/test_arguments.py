import pytest
from src.core import Arguments, GeneratorError
from src.core.arguments import _HANDLER_NOT_FOUND_ERROR, _HANDLER_TAG, _TOO_LITTLE_ARGUMENTS_ERROR

def test_constructor_should_raise_if_less_than_2_arguments():
    ARGS = [ ]

    with pytest.raises(GeneratorError) as error:
        _ = Arguments(ARGS)
    
    assert error.value.message == _TOO_LITTLE_ARGUMENTS_ERROR

def test_constructor_should_raise_if_no_handler_is_passed():
    ARGS = [ "one", "two" ]

    with pytest.raises(GeneratorError) as error:
        _ = Arguments(ARGS)
    
    assert error.value.message == _HANDLER_NOT_FOUND_ERROR

def test_constructor_given_a_filter_filepath_handler_name_and_options_should_instatiate_correctly():
    HANDLER_NAME = "handler"
    FILTER_PATH = "filter_path"
    OPTIONS = [ "option1", "option2" ]
    ARGS = [ FILTER_PATH, _HANDLER_TAG + HANDLER_NAME ] + OPTIONS

    args = Arguments(ARGS)
    
    invocation = args.invocations[0]
    assert args.input_filepath == FILTER_PATH
    assert args.output_filepath == FILTER_PATH
    assert invocation.handler_name == HANDLER_NAME
    assert invocation.options == OPTIONS