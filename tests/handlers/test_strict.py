import pytest
from core import ExpectedError, Operand, Delimiter
from handlers import strict, Context
from handlers.strict import _HANDLER, _RULE, _STRICTNESS_ARG_COUNT_ERROR, _STRICTNESS_ARG_TYPE_ERROR, NAME as STRICT
from test_utilities import create_filter

def test_handle_given_no_options_are_passed_should_raise():
    OPTIONS = []

    with pytest.raises(ExpectedError) as error:
        _ = strict.handle(None, Context(None, OPTIONS))

    assert error.value.message == _STRICTNESS_ARG_COUNT_ERROR.format(_HANDLER, len(OPTIONS))

def test_handle_given_option_is_not_a_digit_should_raise():
    OPTIONS = [ "not_a_digit" ]

    with pytest.raises(ExpectedError) as error:
        _ = strict.handle(None, Context(None, OPTIONS))

    assert error.value.message == _STRICTNESS_ARG_TYPE_ERROR.format(_HANDLER, OPTIONS[0])

def test_handle_given_rule_description_is_not_a_digit_should_raise():
    NON_DIGIT = "not_a_digit"
    FILTER = create_filter(f"{Operand.SHOW} {Delimiter.RULE_START}{STRICT} {NON_DIGIT}")

    with pytest.raises(ExpectedError) as error:
        _ = strict.handle(FILTER.blocks[0], Context(FILTER, [ "1" ]))

    assert error.value.message == _STRICTNESS_ARG_TYPE_ERROR.format(_RULE, NON_DIGIT)
    assert error.value.line_number == FILTER.blocks[0].lines[0].number

def test_handle_given_strictness_in_rule_is_lower_than_options_should_hide():
    STRICTNESS = 1
    FILTER = create_filter(f"{Operand.SHOW} {Delimiter.RULE_START}{STRICT} {STRICTNESS - 1}")

    lines = strict.handle(FILTER.blocks[0], Context(FILTER, [ str(STRICTNESS) ]))

    assert Operand.HIDE in lines[0]

def test_handle_given_strictness_in_rule_is_higher_than_options_should_show():
    STRICTNESS = 1
    FILTER = create_filter(f"{Operand.HIDE} {Delimiter.RULE_START}{STRICT} {STRICTNESS + 1}")

    lines = strict.handle(FILTER.blocks[0], Context(FILTER, [ str(STRICTNESS) ]))

    assert Operand.SHOW in lines[0]