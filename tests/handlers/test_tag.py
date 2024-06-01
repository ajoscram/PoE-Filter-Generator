import pytest
from core import ExpectedError, Operand, Delimiter
from handlers import tag
from handlers.tag import _HANDLER, _RULE, _EMPTY_TAG_ERROR, _WILDCARD, NAME as TAG
from test_utilities import create_filter

def test_handle_given_no_options_were_provided_should_raise():
    OPTIONS = []

    with pytest.raises(ExpectedError) as error:
        tag.handle(None, None, OPTIONS)
    
    assert error.value.message == _EMPTY_TAG_ERROR.format(_HANDLER)

def test_handle_given_a_rule_without_a_description_should_raise():
    FILTER = create_filter(f"{Operand.SHOW} {Delimiter.RULE_START}{TAG}")

    with pytest.raises(ExpectedError) as error:
        tag.handle(FILTER, FILTER.blocks[0], ["tag"])
    
    assert error.value.message == _EMPTY_TAG_ERROR.format(_RULE)
    assert error.value.line_number == FILTER.blocks[0].lines[0].number

def test_handle_given_options_are_more_specific_than_the_rule_should_do_nothing():
    TAG_PATH = [ "1", "2", "3", "4" ]
    FILTER = create_filter(f"{Operand.HIDE} {Delimiter.RULE_START}{TAG} {' '.join(TAG_PATH[:-1])}")

    lines = tag.handle(FILTER, FILTER.blocks[0], TAG_PATH)
    
    assert Operand.HIDE in lines[0]

@pytest.mark.parametrize("option_tag, rule_tag", [ (TAG, TAG), (TAG, _WILDCARD), (_WILDCARD, TAG) ])
def test_handle_given_rule_and_options_are_equivalent_should_show(option_tag: str, rule_tag: str):
    FILTER = create_filter(f"{Operand.HIDE} {Delimiter.RULE_START}{TAG} {rule_tag}")

    lines = tag.handle(FILTER, FILTER.blocks[0], [ option_tag ])

    assert Operand.SHOW in lines[0]

def test_handle_given_rule_and_options_are_different_should_hide():
    FILTER = create_filter(f"{Operand.SHOW} {Delimiter.RULE_START}{TAG} {TAG}")

    lines = tag.handle(FILTER, FILTER.blocks[0], [ f"not_{TAG}" ])

    assert Operand.HIDE in lines[0]