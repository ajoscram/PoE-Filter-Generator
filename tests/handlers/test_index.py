from handlers import index
from test_utilities import create_filter
from core import Delimiter
from handlers.index import _INDEX_RULE_NAME, _SECTION_RULE_NAME, _SUBSECTION_RULE_NAME, _INDEX_HEADER, _INDEX_HINT

def test_handle_given_an_index_section_and_subsection_should_write_them():
    SECTION_NAME = "first_section"
    EXPECTED_SECTION_ID = "1_0"
    SUBSECTION_NAME = "first_subsection"
    EXPECTED_SUBSECTION_ID = "1_1"
    filter = create_filter(
    f"""{Delimiter.RULE_START}{_INDEX_RULE_NAME}
        {Delimiter.RULE_START}{_SECTION_RULE_NAME} {SECTION_NAME}
        {Delimiter.RULE_START}{_SUBSECTION_RULE_NAME} {SUBSECTION_NAME}""")
    
    text = '\n'.join(index.handle(filter, filter.blocks[0], None))

    assert text.count(_INDEX_HEADER) == 1
    assert text.count(_INDEX_HINT) == 1
    assert text.count(SECTION_NAME) == 3 # the rule, the section and the index
    assert text.count(EXPECTED_SECTION_ID) == 2 # the section and the index
    assert text.count(SUBSECTION_NAME) == 3 # the rule, the section and the index
    assert text.count(EXPECTED_SUBSECTION_ID) == 2 # the section and the index
    assert index._index == None # the index should be reset after the invocation

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
    
    text = '\n'.join(index.handle(filter, filter.blocks[0], None))

    assert text.count(EXPECTED_SECTION_ID) == 2 # the section and the index
    assert text.count(EXPECTED_SUBSECTION_ID) == 2 # the section and the index

def test_handle_given_index_with_description_should_add_it():
    DESCRIPTION = "description"
    filter = create_filter(f"{Delimiter.RULE_START}{_INDEX_RULE_NAME} {DESCRIPTION}")

    text = '\n'.join(index.handle(filter, filter.blocks[0], None))

    assert DESCRIPTION in text