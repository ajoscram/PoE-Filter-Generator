import pytest
from core import ExpectedError, Line, Operand, Delimiter, Operator, BLOCK_STARTERS
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
    ("    ", Operand.CLASS, Operator.EQUALS, "", ""),
    ("    ", Operand.AREA_LEVEL, "", "-1", ""),
    ("    ", Operand.AREA_LEVEL, "", "1", ""),
    ("    ", Operand.CLASS, Operator.EQUALS, '"Body Armours"', ""),
    ("    ", Operand.CLASS, f"{Operator.EQUALS}2", '"Body Armours"', ""),
    ("    ", Operand.CLASS, Operator.EQUALS, '"Body Armours"', f"{Delimiter.COMMENT_START}this is a comment"),
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

_SUBSTRING = "substring"
_CONTAINS_LINES = [
    _SUBSTRING,
    f"{Delimiter.COMMENT_START} {_SUBSTRING}",
    f"operand {Operator.EQUALS} {_SUBSTRING}",
    f"operand {Operator.EQUALS} another_string"
]
@pytest.mark.parametrize("text", _CONTAINS_LINES)
def test_contains_given_a_string_should_return_as_expected(text: str):
    line = Line(text, _LINE_NUMBER)

    result = _SUBSTRING in line

    assert result == (_SUBSTRING in text)


@pytest.mark.parametrize("text", [ f"{Operand.CLASS} {Operator.EQUALS} Classname", "" ])
def test_has_filter_info_should_return_whether_or_not_line_has_filter_info(text: str):
    line = Line(text, _LINE_NUMBER)

    result = line.has_filter_info()

    assert result == (text != "")

@pytest.mark.parametrize("text", [ f"{Delimiter.RULE_START}rule_name", "" ])
def test_has_rules_should_return_whether_or_not_line_has_rules(text: str):
    line = Line(text, _LINE_NUMBER)

    result = line.has_rules()

    assert result == (Delimiter.RULE_START in text)
    assert not line.has_comment()

@pytest.mark.parametrize("text", [ f"{Delimiter.COMMENT_START} a comment", "" ])
def test_has_comment_should_return_whether_or_not_line_has_comment(text: str):
    line = Line(text, _LINE_NUMBER)

    result = line.has_comment()

    assert result == (Delimiter.COMMENT_START in text)
    assert not line.has_rules()

@pytest.mark.parametrize("text", [
    f"{Operand.CLASS} {Operator.EQUALS} Classname",
    f"{Delimiter.COMMENT_START} a comment",
    f"{Delimiter.RULE_START}rule_name",
    "\t",
    " ",
    "" ])
def test_is_empty_should_return_whether_or_not_line_has_content(text: str):
    line = Line(text, _LINE_NUMBER)

    result = line.is_empty()

    assert result == (text.isspace() or text == "")

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