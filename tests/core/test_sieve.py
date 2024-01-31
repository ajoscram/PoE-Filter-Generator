import pytest
from core import ExpectedError, SHOW, EQUALS, CONTAINS, LESS, LESS_EQUALS, GREATER, GREATER_EQUALS, NOT_EQUALS, NOT_CONTAINS
from core.sieve import _BOOL_OPERATOR_ERROR, _INT_OPERATOR_ERROR, _INT_VALUE_ERROR, _STR_OPERATOR_ERROR, _BOOL_VALUE_ERROR
from test_utilities import create_sieve_for_text

_STR_OPERAND = "StrOperand"
_STR_VALUE = "value"

_INT_OPERAND = "IntOperand"
_INT_VALUE = 2

_BOOL_OPERAND = "BoolOperand"
_BOOL_VALUE = True

_PATTERN = { _STR_OPERAND: _STR_VALUE, _INT_OPERAND: _INT_VALUE, _BOOL_OPERAND: _BOOL_VALUE }

def test_in_operator_given_empty_pattern_should_return_true():
    sieve = create_sieve_for_text(f'{_STR_OPERAND} {EQUALS} "some value"')

    assert {} in sieve

def test_in_operator_given_no_values_should_return_true():
    sieve = create_sieve_for_text(f'{_STR_OPERAND} {EQUALS}')

    assert { _STR_OPERAND: "any_value" } in sieve

@pytest.mark.parametrize("value, expected_result", [ ("", True), ("value", False) ])
def test_in_operator_given_None_should_return_expectedly(value: str, expected_result: bool):
    sieve = create_sieve_for_text(f'{SHOW} {value}')

    result = { SHOW: None } in sieve

    assert result == expected_result

@pytest.mark.parametrize("operator, expected_result", [
    (EQUALS, True),
    (CONTAINS, True),
    ("", True),
    (NOT_EQUALS, False),
    (NOT_CONTAINS, False),
])
def test_in_operator_given_string_value_and_a_valid_operator_should_return_expectedly(
    operator: str, expected_result: bool):
    
    sieve = create_sieve_for_text(f'{_STR_OPERAND} {operator} "{_STR_VALUE}"')

    result = _PATTERN in sieve

    assert result == expected_result

def test_in_operator_given_invalid_str_operator_should_raise():
    INVALID_OPERATOR = GREATER_EQUALS
    sieve = create_sieve_for_text(f'{_STR_OPERAND} {INVALID_OPERATOR} {_STR_VALUE}')

    with pytest.raises(ExpectedError) as error:
        _PATTERN in sieve

    assert error.value.message == _STR_OPERATOR_ERROR.format(INVALID_OPERATOR)
    assert error.value.line_number == 0

@pytest.mark.parametrize("filter_value, operator, expected_result", [
    (True, EQUALS, True),
    (False, CONTAINS, False),
    (True, "", True),
    (False, NOT_EQUALS, True),
    (True, NOT_CONTAINS, False),
])
def test_in_operator_given_bool_should_return_expectedly(filter_value: bool, operator: str, expected_result: bool):
    sieve = create_sieve_for_text(f'{_BOOL_OPERAND} {operator} {filter_value}')

    result = _PATTERN in sieve

    assert result == expected_result

def test_in_operator_given_non_bool_value_should_raise():
    INVALID_VALUE = "NotBool"
    sieve = create_sieve_for_text(f'{_BOOL_OPERAND} {EQUALS} {INVALID_VALUE}')

    with pytest.raises(ExpectedError) as error:
        _PATTERN in sieve
    
    assert error.value.message == _BOOL_VALUE_ERROR.format(_BOOL_OPERAND, INVALID_VALUE)
    assert error.value.line_number == 0

def test_in_operator_given_invalid_bool_operator_should_raise():
    INVALID_OPERATOR = GREATER
    sieve = create_sieve_for_text(f'{_BOOL_OPERAND} {INVALID_OPERATOR} {True}')

    with pytest.raises(ExpectedError) as error:
        _PATTERN in sieve
    
    assert error.value.message == _BOOL_OPERATOR_ERROR.format(INVALID_OPERATOR)
    assert error.value.line_number == 0

@pytest.mark.parametrize("filter_value, operator", [
    (_INT_VALUE - 1, GREATER_EQUALS),
    (_INT_VALUE - 1, GREATER),
    (_INT_VALUE + 1, LESS_EQUALS),
    (_INT_VALUE + 1, LESS),
    (_INT_VALUE, EQUALS),
    (_INT_VALUE, CONTAINS),
    (_INT_VALUE, ""),
    (_INT_VALUE + 1, NOT_EQUALS),
    (_INT_VALUE + 1, NOT_CONTAINS),
])
def test_in_operator_given_int_value_and_a_valid_operator_should_return_expectedly(
    filter_value: int, operator: str):
    
    sieve = create_sieve_for_text(f'{_INT_OPERAND} {operator} {filter_value}')

    assert _PATTERN in sieve

def test_in_operator_given_int_value_doesnt_apply_should_return_false():
    sieve = create_sieve_for_text(f'{_INT_OPERAND} {GREATER} {_INT_VALUE}')

    assert _PATTERN not in sieve

def test_in_operator_given_invalid_int_operator_should_raise():
    INVALID_OPERATOR = "invalid_operator"
    sieve = create_sieve_for_text(f'{_INT_OPERAND} {LESS} {_INT_VALUE}')
    sieve._lines_by_operand[_INT_OPERAND][0].operator = INVALID_OPERATOR

    with pytest.raises(ExpectedError) as error:
        _PATTERN in sieve

    assert error.value.message == _INT_OPERATOR_ERROR.format(INVALID_OPERATOR)
    assert error.value.line_number == 0

@pytest.mark.parametrize("values", [ "0 2",  "not_int"])
def test_in_operator_given_invalid_int_values_should_raise(values: str):
    sieve = create_sieve_for_text(f'{_INT_OPERAND} {EQUALS} {values}')

    with pytest.raises(ExpectedError) as error:
        _PATTERN in sieve

    assert error.value.message == _INT_VALUE_ERROR.format(_INT_OPERAND, values)
    assert error.value.line_number == 0

def test_in_operator_given_multiple_lines_with_the_same_operator_should_check_all_of_them():
    sieve = create_sieve_for_text(
        f'''{_STR_OPERAND} {EQUALS} {_STR_VALUE}
            {_STR_OPERAND} {EQUALS} "another value"''')
    
    assert _PATTERN not in sieve