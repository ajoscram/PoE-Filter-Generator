import pytest
from core import Delimiter, ExpectedError
from handlers import index
from handlers.index import _SUBSECTION_MISSING_PARENT_SECTION_ERROR, IndexContext, _INDEX_RULE_NAME, _SECTION_RULE_NAME, _SUBSECTION_RULE_NAME, _INDEX_HEADER, _INDEX_HINT
from test_utilities import create_filter

def test_handle_given_an_index_section_and_subsection_should_write_them():
    SECTION_NAME = "first_section"
    EXPECTED_SECTION_ID = "1_0"
    SUBSECTION_NAME = "first_subsection"
    EXPECTED_SUBSECTION_ID = "1_1"
    filter = create_filter(
    f"""{Delimiter.RULE_START}{_INDEX_RULE_NAME}
        {Delimiter.RULE_START}{_SECTION_RULE_NAME} {SECTION_NAME}
        {Delimiter.RULE_START}{_SUBSECTION_RULE_NAME} {SUBSECTION_NAME}""")
    
    text = '\n'.join(index.handle(filter.blocks[0], IndexContext(filter, [])))

    assert text.count(_INDEX_HEADER) == 1
    assert text.count(_INDEX_HINT) == 1
    assert text.count(SECTION_NAME) == 3 # the rule, the section and the index
    assert text.count(EXPECTED_SECTION_ID) == 2 # the section and the index
    assert text.count(SUBSECTION_NAME) == 3 # the rule, the section and the index
    assert text.count(EXPECTED_SUBSECTION_ID) == 2 # the section and the index

def test_handle_given_enough_sections_to_cause_id_padding_should_add_the_padding():
    EXPECTED_SUBSECTION_ID = "01_00"
    EXPECTED_SECTION_ID = "10_10"
    filter_contents = f"{Delimiter.RULE_START}{_INDEX_RULE_NAME}\n"
    filter_contents += "\n".join(
        f"{Delimiter.RULE_START}{_SECTION_RULE_NAME} section_{i+1}" for i in range(10))
    filter_contents += "\n"
    filter_contents += "\n".join(
        f"{Delimiter.RULE_START}{_SUBSECTION_RULE_NAME} subsection_{i+1}" for i in range(10))
    filter = create_filter(filter_contents)
    
    text = '\n'.join(index.handle(filter.blocks[0], IndexContext(filter, [])))

    assert text.count(EXPECTED_SECTION_ID) == 2 # the section and the index
    assert text.count(EXPECTED_SUBSECTION_ID) == 2 # the section and the index

def test_handle_given_multiple_subsections_should_render_the_numbers_appropriately():
    EXPECTED_SECOND_SUBSECTION_ID = "1_2"
    
    filter = create_filter(
    f"""{Delimiter.RULE_START}{_INDEX_RULE_NAME}
        {Delimiter.RULE_START}{_SECTION_RULE_NAME} section
        {Delimiter.RULE_START}{_SUBSECTION_RULE_NAME} first_subsection
        {Delimiter.RULE_START}{_SUBSECTION_RULE_NAME} second_subsection""")
    
    text = '\n'.join(index.handle(filter.blocks[0], IndexContext(filter, [])))

    assert text.count(EXPECTED_SECOND_SUBSECTION_ID) == 2 # the section and the index

def test_handle_given_index_with_description_should_add_it():
    DESCRIPTION = "description"
    filter = create_filter(f"{Delimiter.RULE_START}{_INDEX_RULE_NAME} {DESCRIPTION}")

    text = '\n'.join(index.handle(filter.blocks[0], IndexContext(filter, [])))

    assert DESCRIPTION in text

def test_handle_given_subsection_before_any_parent_section_should_raise():
    SUBSECTION_NAME = "first_subsection"
    filter = create_filter(f"{Delimiter.RULE_START}{_SUBSECTION_RULE_NAME} {SUBSECTION_NAME}")

    with pytest.raises(ExpectedError) as error:
        index.handle(filter.blocks[0], IndexContext(filter, []))
    
    assert error.value.message == _SUBSECTION_MISSING_PARENT_SECTION_ERROR.format(SUBSECTION_NAME)
    assert error.value.line_number == filter.blocks[0].lines[0].number