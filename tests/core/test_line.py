import pytest

from src.core.constants import CLASS, COMMENT_START, BLOCK_STARTERS, RULE_SEPARATOR, RULE_START
from src.core.line import _BOOL_VALUE_ERROR, _INT_VALUE_ERROR, _MULTILINE_STRING_ERROR
from src.core import GeneratorError, Line

LINE_NUMBER = 1

def test_constructor_given_text_has_linebreak_should_raise():
    TEXT = "a\nb"

    with pytest.raises(GeneratorError) as error:
        _ = Line(TEXT, LINE_NUMBER)
    
    assert error.value.message == _MULTILINE_STRING_ERROR
    assert error.value.line_number == LINE_NUMBER

LINE_PARTS = [
    ("    ", CLASS, "", "", ""),
    ("    ", CLASS, "==", "", ""),
    ("    ", CLASS, "==", '"Body Armours"', ""),
    ("    ", CLASS, "==2", '"Body Armours"', ""),
    ("    ", CLASS, "==", '"Body Armours"', f"{COMMENT_START}this is a comment"),
]
@pytest.mark.parametrize("indent, operand, operator, value, comment", LINE_PARTS)
def test_constructor_given_a_valid_line_text_should_parse_it_into_its_parts(
    indent: str, operand: str, operator: str, value: str, comment: str):
    TEXT = f"{indent}{operand} {operator} {value} {comment}"

    line = Line(TEXT, LINE_NUMBER)

    assert line.indentation == indent
    assert line.operand == operand
    assert line.operator == operator
    assert value in line.values or value == ''
    assert line.comment == comment

@pytest.mark.parametrize("operand, expected", [ (BLOCK_STARTERS[0], True), ("not_a_block_starter", False) ])
def test_is_block_starter_given_an_operand_should_return_as_expected(operand: str, expected: bool):
    line = Line(operand, LINE_NUMBER)

    is_block_starter = line.is_block_starter()

    assert is_block_starter == expected

@pytest.mark.parametrize("value_str, expected", [ ("true", True), ("false", False) ])
def test_get_value_as_bool_given_a_single_bool_value_should_return_the_bool(value_str: str, expected: bool):
    TEXT = f"operand {value_str}"
    line = Line(TEXT, LINE_NUMBER)
    
    actual = line.get_value_as_bool()

    assert actual == expected

@pytest.mark.parametrize("values", [ "non_bool_value", "True False" ])
def test_get_value_as_bool_given_incorrect_values_should_raise(values: str):
    TEXT = "operand " + values
    line = Line(TEXT, LINE_NUMBER)
    
    with pytest.raises(GeneratorError) as error:
        _ = line.get_value_as_bool()

    assert error.value.message == _BOOL_VALUE_ERROR
    assert error.value.line_number == LINE_NUMBER

def test_get_value_as_int_given_a_single_int_value_should_return_the_int():
    EXPECTED_VALUE = 3
    TEXT = f"operand > {EXPECTED_VALUE}"
    line = Line(TEXT, LINE_NUMBER)
    
    actual_value = line.get_value_as_int()

    assert actual_value == EXPECTED_VALUE

@pytest.mark.parametrize("values", [ "non_int_value", "2 3" ])
def test_get_value_as_int_given_incorrect_values_should_raise(values: str):
    TEXT = "operand == " + values
    line = Line(TEXT, LINE_NUMBER)
    
    with pytest.raises(GeneratorError) as error:
        _ = line.get_value_as_int()

    assert error.value.message == _INT_VALUE_ERROR
    assert error.value.line_number == LINE_NUMBER

@pytest.mark.parametrize("exclude_comments, expected", [ (False, True), (True, False) ])
def test_contains_given_a_pattern_should_return_as_expected(exclude_comments: bool, expected: bool):
    PATTERN_TO_FIND = "pattern"
    TEXT = f"operand {COMMENT_START}{PATTERN_TO_FIND}"
    line = Line(TEXT, LINE_NUMBER)

    result = line.contains(PATTERN_TO_FIND, exclude_comments)

    assert result == expected

def test_get_rules_given_a_name_should_get_rules_with_that_name():
    RULE_NAME = "rule_name"
    TEXT = f"operand {RULE_START}{RULE_NAME} {RULE_SEPARATOR}some_other_rule"
    line = Line(TEXT, LINE_NUMBER)

    rules = line.get_rules(RULE_NAME)

    assert len(rules) == 1
    assert rules[0].name == RULE_NAME

def test_comment_out_should_comment_out_the_line():
    TEXT = "operand == value"
    line = Line(TEXT, LINE_NUMBER)

    line.comment_out()

    assert line.operand == ""
    assert line.operator == ""
    assert line.values == []
    assert TEXT in line.comment

def test_str_overload_should_return_the_input_text():
    TEXT = f"operand == value {COMMENT_START} a comment"
    line = Line(TEXT, LINE_NUMBER)

    line_str = str(line)

    assert line_str == TEXT