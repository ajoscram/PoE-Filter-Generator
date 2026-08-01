import pytest
from core import Delimiter, Rule, ExpectedError
from core.rule import _EMPTY_RULE_ERROR

_LINE_NUMBER = 1
_NAME = "name"
_DESCRIPTION = "description"

def test_constructor_given_valid_parameters_should_instaitate_correctly():

    rule = Rule(_LINE_NUMBER, _NAME, _DESCRIPTION)

    assert rule.line_number == _LINE_NUMBER
    assert rule.name == _NAME
    assert rule.description == _DESCRIPTION

def test_extract_given_text_without_rules_should_return_an_empty_list():
    TEXT = f"line {Delimiter.COMMENT_START}comment"

    rules = Rule.extract(_LINE_NUMBER, TEXT)

    assert rules == []

def test_extract_given_an_empty_rule_should_raise():
    TEXT_WITH_EMPTY_RULE = f"line {Delimiter.RULE_START}"

    with pytest.raises(ExpectedError) as error:
        Rule.extract(_LINE_NUMBER, TEXT_WITH_EMPTY_RULE)
    
    assert error.value.message == _EMPTY_RULE_ERROR
    assert error.value.line_number == _LINE_NUMBER

def test_extract_given_a_rule_without_description_should_return_an_empty_description():
    RULE_TEXT_WITHOUT_DESCRIPTION = f"{Delimiter.RULE_START}rule"

    rule = Rule.extract(_LINE_NUMBER, RULE_TEXT_WITHOUT_DESCRIPTION)[0]

    assert rule.description == ""

def test_extract_given_rules_should_return_a_list_of_them():
    TEXT = f"line {Delimiter.RULE_START}{_NAME} {_DESCRIPTION} {Delimiter.RULE_SEPARATOR}{_NAME} {_DESCRIPTION}"

    rules = Rule.extract(_LINE_NUMBER, TEXT)

    assert len(rules) == 2
    for rule in rules:
        assert rule.line_number == _LINE_NUMBER
        assert rule.name == _NAME
        assert rule.description == _DESCRIPTION

def test_extract_given_comment_rule_should_consume_rules_after_it():
    DESCRIPTION = f"comment {Delimiter.RULE_SEPARATOR}{_NAME} {_DESCRIPTION}"
    TEXT = f"line {Delimiter.COMMENT_RULE_START} {DESCRIPTION}"

    rules = Rule.extract(_LINE_NUMBER, TEXT)

    assert len(rules) == 1
    assert rules[0].line_number == _LINE_NUMBER
    assert rules[0].name == Delimiter.COMMENT_START
    assert rules[0].description == DESCRIPTION

def test_extract_given_comment_rule_should_not_consume_rules_before_it():
    TEXT = f"line {Delimiter.RULE_START}{_NAME} {_DESCRIPTION} {Delimiter.RULE_SEPARATOR}{Delimiter.COMMENT_START} comment"

    rules = Rule.extract(_LINE_NUMBER, TEXT)

    assert len(rules) == 2