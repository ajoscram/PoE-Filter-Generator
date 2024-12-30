import pytest
from core import Delimiter, ExpectedError
from handlers import alias
from handlers.alias import _ALIAS_ENTRY_SEPARATOR, _ALIAS_NAME_ERROR_DESCRIPTOR, _ALIAS_PART_SEPARATOR, _CONTAINED_ALIAS_NAME_ERROR, _CONTAINS_ERROR_DESCRIPTOR, _DUPLICATE_ALIAS_NAME_ERROR, _EMPTY_PARAMETER_ERROR, _ALIAS_FORMAT_ERROR, _IS_CONTAINED_BY_ERROR_DESCRIPTOR, _REPLACEMENT_ERROR_DESCRIPTOR, _RULE_SOURCE_NAME, NAME as ALIAS
from test_utilities import create_filter

_ALIAS_NAME = "NAME"
_ALIAS_REPLACEMENT = "replacement"

def test_handle_given_an_alias_in_options_should_replace():
    OPTIONS = [ _ALIAS_NAME, _ALIAS_PART_SEPARATOR, _ALIAS_REPLACEMENT ]
    filter = create_filter(f"{_ALIAS_NAME}")
    
    lines = alias.handle(filter, filter.blocks[0], OPTIONS)

    assert _ALIAS_REPLACEMENT in lines[0]
    assert alias._aliases == None #  the list of aliases should be reset after the invocation

def test_handle_given_multiple_alias_should_replace_all():
    _ALIAS_NAME_2 = "_ALIAS_2"
    _ALIAS_REPLACEMENT_2 = "replacement_2"
    OPTIONS = [
        _ALIAS_NAME, _ALIAS_PART_SEPARATOR, _ALIAS_REPLACEMENT,
        _ALIAS_ENTRY_SEPARATOR,
        _ALIAS_NAME_2, _ALIAS_PART_SEPARATOR, _ALIAS_REPLACEMENT_2 ]
    filter = create_filter(
    f"""{_ALIAS_NAME}
        {_ALIAS_NAME_2}""")
    
    lines = alias.handle(filter, filter.blocks[0], OPTIONS)

    assert _ALIAS_REPLACEMENT in lines[0]
    assert _ALIAS_REPLACEMENT_2 in lines[1]

def test_handle_given_an_alias_in_a_rule_should_replace():
    filter = create_filter(
    f"""{Delimiter.RULE_START}{ALIAS} {_ALIAS_NAME} {_ALIAS_PART_SEPARATOR} {_ALIAS_REPLACEMENT}
        {_ALIAS_NAME}""")
    
    lines = alias.handle(filter, filter.blocks[0], [])

    assert _ALIAS_NAME in lines[0] # text in alias rules should not be replaced
    assert _ALIAS_REPLACEMENT in lines[1]

def test_handle_given_incorrect_description_format_should_raise():
    DESCRIPTION = "incorrect description"
    filter = create_filter(f"{Delimiter.RULE_START}{ALIAS} {DESCRIPTION}")

    with pytest.raises(ExpectedError) as error:
        _ = alias.handle(filter, filter.blocks[0], [])

    assert error.value.line_number == filter.blocks[0].lines[0].number
    assert error.value.message == _ALIAS_FORMAT_ERROR.format(DESCRIPTION)

@pytest.mark.parametrize("name, replacement, error_descriptor", [
    ("", _ALIAS_REPLACEMENT, _ALIAS_NAME_ERROR_DESCRIPTOR),
    (_ALIAS_NAME, "", _REPLACEMENT_ERROR_DESCRIPTOR)
])
def test_handle_given_empty_alias_part_should_raise(name: str, replacement: str, error_descriptor: str):
    DESCRIPTION = f"{name}{_ALIAS_PART_SEPARATOR}{replacement}"
    filter = create_filter(f"{Delimiter.RULE_START}{ALIAS} {DESCRIPTION}")

    with pytest.raises(ExpectedError) as error:
        _ = alias.handle(filter, filter.blocks[0], [])
    
    assert error.value.line_number == filter.blocks[0].lines[0].number
    assert error.value.message == _EMPTY_PARAMETER_ERROR.format(error_descriptor, DESCRIPTION)

def test_handle_given_duplicate_alias_name_should_raise():
    filter = create_filter(
    f"""{Delimiter.RULE_START}{ALIAS} {_ALIAS_NAME} {_ALIAS_PART_SEPARATOR} {_ALIAS_REPLACEMENT}
        {Delimiter.RULE_START}{ALIAS} {_ALIAS_NAME} {_ALIAS_PART_SEPARATOR} other replacement""")
    
    with pytest.raises(ExpectedError) as error:
        _ = alias.handle(filter, filter.blocks[0], [])
    
    assert error.value.line_number == filter.blocks[0].lines[1].number
    assert error.value.message == _DUPLICATE_ALIAS_NAME_ERROR.format(
        _ALIAS_NAME,
        _RULE_SOURCE_NAME.format(filter.blocks[0].lines[0].number))

@pytest.mark.parametrize("first_name, error_name, contained_descriptor", [
    (_ALIAS_NAME, _ALIAS_NAME[-1], _IS_CONTAINED_BY_ERROR_DESCRIPTOR),
    (_ALIAS_NAME[-1], _ALIAS_NAME, _CONTAINS_ERROR_DESCRIPTOR),
])
def test_handle_given_contained_alias_names_should_raise(first_name: str, error_name: str, contained_descriptor: str):
    filter = create_filter(
    f"""{Delimiter.RULE_START}{ALIAS} {first_name} {_ALIAS_PART_SEPARATOR} {_ALIAS_REPLACEMENT}
        {Delimiter.RULE_START}{ALIAS} {error_name} {_ALIAS_PART_SEPARATOR} {_ALIAS_REPLACEMENT}""")
    
    with pytest.raises(ExpectedError) as error:
        _ = alias.handle(filter, filter.blocks[0], [])

    assert error.value.line_number == filter.blocks[0].lines[1].number
    assert error.value.message == _CONTAINED_ALIAS_NAME_ERROR.format(
        error_name,
        contained_descriptor,
        first_name,
        _RULE_SOURCE_NAME.format(filter.blocks[0].lines[0].number))