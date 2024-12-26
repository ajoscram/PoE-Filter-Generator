import pytest
from core import ExpectedError, Line, Operand, Delimiter, BLOCK_STARTERS
from core.line import _MULTILINE_STRING_ERROR

_LINE_NUMBER = 1

def test_constructor_given_text_has_linebreak_should_raise():
    TEXT = "a\nb"

    with pytest.raises(ExpectedError) as error:
        _ = Line(TEXT, _LINE_NUMBER)
    
    assert error.value.message == _MULTILINE_STRING_ERROR
    assert error.value.line_number == _LINE_NUMBER

_LINE_PARTS = [
    ("    ", Operand.CLASS, "", "", ""),
    ("    ", Operand.CLASS, "", '""', ""),
    ("    ", Operand.CLASS, "==", "", ""),
    ("    ", Operand.AREA_LEVEL, "", "-1", ""),
    ("    ", Operand.AREA_LEVEL, "", "1", ""),
    ("    ", Operand.CLASS, "==", '"Body Armours"', ""),
    ("    ", Operand.CLASS, "==2", '"Body Armours"', ""),
    ("    ", Operand.CLASS, "==", '"Body Armours"', f"{Delimiter.COMMENT_START}this is a comment"),
]
@pytest.mark.parametrize("indent, operand, operator, value, comment", _LINE_PARTS)
def test_constructor_given_a_valid_line_text_should_parse_it_into_its_parts(
    indent: str, operand: str, operator: str, value: str, comment: str):
    TEXT = f"{indent}{operand} {operator} {value} {comment}"

    line = Line(TEXT, _LINE_NUMBER)

    assert line.indentation == indent
    assert line.operand == operand
    assert line.operator == operator
    assert value in line.values or value == ''
    assert line.comment == comment

@pytest.mark.parametrize("operand, expected", [ (BLOCK_STARTERS[0], True), ("not_a_block_starter", False) ])
def test_is_block_starter_given_an_operand_should_return_as_expected(operand: str, expected: bool):
    line = Line(operand, _LINE_NUMBER)

    is_block_starter = line.is_block_starter()

    assert is_block_starter == expected

@pytest.mark.parametrize("exclude_comments, expected", [ (False, True), (True, False) ])
def test_contains_given_a_string_should_return_as_expected(exclude_comments: bool, expected: bool):
    STRING = "string"
    TEXT = f"operand {Delimiter.COMMENT_START}{STRING}"
    line = Line(TEXT, _LINE_NUMBER)

    result = line.contains(STRING, exclude_comments)

    assert result == expected

@pytest.mark.parametrize("exclude_comments", [ False, True ])
def test_is_empty_given_(exclude_comments: bool):
    EXPECTED = exclude_comments
    TEXT = f"    {Delimiter.COMMENT_START} comment"
    line = Line(TEXT, _LINE_NUMBER)

    result = line.is_empty(exclude_comments)

    assert result == EXPECTED

def test_get_rules_given_a_name_should_get_rules_with_that_name():
    RULE_NAME = "rule_name"
    TEXT = f"operand {Delimiter.RULE_START}{RULE_NAME} {Delimiter.RULE_SEPARATOR}some_other_rule"
    line = Line(TEXT, _LINE_NUMBER)

    rules = line.get_rules(RULE_NAME)

    assert len(rules) == 1
    assert rules[0].name == RULE_NAME

def test_comment_out_should_comment_out_the_line():
    TEXT = "operand == value"
    line = Line(TEXT, _LINE_NUMBER)

    line.comment_out()

    assert line.operand == ""
    assert line.operator == ""
    assert line.values == []
    assert TEXT in line.comment

def test_str_overload_should_return_the_input_text():
    TEXT = f"operand == value {Delimiter.COMMENT_START} a comment"
    line = Line(TEXT, _LINE_NUMBER)

    line_str = str(line)

    assert line_str == TEXT