import pytest
from core.constants import COMMENT_START, RULE_SEPARATOR, RULE_START
from core.rule import _EMPTY_RULE_ERROR
from core import Rule, ExpectedError

_LINE_NUMBER = 1

def test_constructor_given_valid_parameters_should_instaitate_correctly():
    NAME = "name"
    DESCRIPTION = "description"

    rule = Rule(_LINE_NUMBER, NAME, DESCRIPTION)

    assert rule.line_number == _LINE_NUMBER
    assert rule.name == NAME
    assert rule.description == DESCRIPTION

def test_extract_given_text_without_rules_should_return_an_empty_list():
    TEXT = f"line {COMMENT_START}comment"

    rules = Rule.extract(_LINE_NUMBER, TEXT)

    assert rules == []

def test_extract_given_an_empty_rule_should_raise():
    TEXT_WITH_EMPTY_RULE = f"line {RULE_START}"

    with pytest.raises(ExpectedError) as error:
        Rule.extract(_LINE_NUMBER, TEXT_WITH_EMPTY_RULE)
    
    assert error.value.message == _EMPTY_RULE_ERROR
    assert error.value.line_number == _LINE_NUMBER

def test_extract_given_a_rule_without_description_should_return_an_empty_description():
    RULE_TEXT_WITHOUT_DESCRIPTION = f"{RULE_START}rule"

    rule = Rule.extract(_LINE_NUMBER, RULE_TEXT_WITHOUT_DESCRIPTION)[0]

    assert rule.description == ""

def test_extract_given_rules_should_return_a_list_of_them():
    RULE_NAME = "name"
    RULE_DESCRIPTION = "description"
    RULE_TEXT = f"line {RULE_START}{RULE_NAME} {RULE_DESCRIPTION} {RULE_SEPARATOR}{RULE_NAME} {RULE_DESCRIPTION}"

    rules = Rule.extract(_LINE_NUMBER, RULE_TEXT)

    assert len(rules) == 2
    for rule in rules:
        assert rule.line_number == _LINE_NUMBER
        assert rule.name == RULE_NAME
        assert rule.description == RULE_DESCRIPTION