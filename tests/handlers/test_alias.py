import pytest
from core import ExpectedError, RULE_START
from handlers import alias
from handlers.alias import _ALIAS_NAME_ERROR_DESCRIPTOR, _ALIAS_SEPARATOR, _CONTAINED_ALIAS_NAME_ERROR, _CONTAINS_ERROR_DESCRIPTOR, _DUPLICATE_ALIAS_NAME_ERROR, _EMPTY_PARAMETER_ERROR, _INCORRECT_RULE_FORMAT_ERROR, _IS_CONTAINED_BY_ERROR_DESCRIPTOR, _REPLACEMENT_ERROR_DESCRIPTOR, NAME as ALIAS
from test_utilities import create_filter

_ALIAS_NAME = "NAME"
_ALIAS_REPLACEMENT = "replacement"

@pytest.fixture(autouse=True)
def setup():
    alias._aliases = None

def test_handle_given_an_alias_should_replace_all_non_alias_rule_text():
    filter = create_filter(
    f"""{RULE_START}{ALIAS} {_ALIAS_NAME} {_ALIAS_SEPARATOR} {_ALIAS_REPLACEMENT}
        {_ALIAS_NAME}""")
    
    lines = alias.handle(filter, filter.blocks[0], None)

    assert _ALIAS_NAME in lines[0] # text in alias rules should not be replaced
    assert _ALIAS_REPLACEMENT in lines[1]

def test_handle_given_incorrect_description_format_should_raise():
    DESCRIPTION = "incorrect description"
    filter = create_filter(f"{RULE_START}{ALIAS} {DESCRIPTION}")

    with pytest.raises(ExpectedError) as error:
        _ = alias.handle(filter, filter.blocks[0], None)

    assert error.value.line_number == filter.blocks[0].lines[0].number
    assert error.value.message == _INCORRECT_RULE_FORMAT_ERROR.format(DESCRIPTION)

@pytest.mark.parametrize("name, replacement, error_descriptor", [
    ("", _ALIAS_REPLACEMENT, _ALIAS_NAME_ERROR_DESCRIPTOR),
    (_ALIAS_NAME, "", _REPLACEMENT_ERROR_DESCRIPTOR)
])
def test_handle_given_empty_alias_part_should_raise(name: str, replacement: str, error_descriptor: str):
    DESCRIPTION = f"{name}{_ALIAS_SEPARATOR}{replacement}"
    filter = create_filter(f"{RULE_START}{ALIAS} {DESCRIPTION}")

    with pytest.raises(ExpectedError) as error:
        _ = alias.handle(filter, filter.blocks[0], None)
    
    assert error.value.line_number == filter.blocks[0].lines[0].number
    assert error.value.message == _EMPTY_PARAMETER_ERROR.format(error_descriptor, DESCRIPTION)

def test_handle_given_duplicate_alias_name_should_raise():
    filter = create_filter(
    f"""{RULE_START}{ALIAS} {_ALIAS_NAME} {_ALIAS_SEPARATOR} {_ALIAS_REPLACEMENT}
        {RULE_START}{ALIAS} {_ALIAS_NAME} {_ALIAS_SEPARATOR} other replacement""")
    
    with pytest.raises(ExpectedError) as error:
        _ = alias.handle(filter, filter.blocks[0], None)
    
    assert error.value.line_number == filter.blocks[0].lines[1].number
    assert error.value.message == _DUPLICATE_ALIAS_NAME_ERROR.format(
        _ALIAS_NAME, filter.blocks[0].lines[0].number)

@pytest.mark.parametrize("first_name, error_name, contained_descriptor", [
    (_ALIAS_NAME, _ALIAS_NAME[-1], _IS_CONTAINED_BY_ERROR_DESCRIPTOR),
    (_ALIAS_NAME[-1], _ALIAS_NAME, _CONTAINS_ERROR_DESCRIPTOR),
])
def test_handle_given_contained_alias_names_should_raise(first_name: str, error_name: str, contained_descriptor: str):
    filter = create_filter(
    f"""{RULE_START}{ALIAS} {first_name} {_ALIAS_SEPARATOR} {_ALIAS_REPLACEMENT}
        {RULE_START}{ALIAS} {error_name} {_ALIAS_SEPARATOR} {_ALIAS_REPLACEMENT}""")
    
    with pytest.raises(ExpectedError) as error:
        _ = alias.handle(filter, filter.blocks[0], None)
    
    assert error.value.line_number == filter.blocks[0].lines[1].number
    assert error.value.message == _CONTAINED_ALIAS_NAME_ERROR.format(
        error_name, contained_descriptor, first_name, filter.blocks[0].lines[0].number)