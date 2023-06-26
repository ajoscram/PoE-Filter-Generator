from handlers import index
from test_utilities import create_filter
from core.constants import RULE_START
from handlers.index import _INDEX_RULE_NAME, _SECTION_RULE_NAME, _SUBSECTION_RULE_NAME, _INDEX_HEADER, _INDEX_HINT

def test_handle_given_an_index_section_and_subsection_should_write_them():
    SECTION_NAME = "first_section"
    EXPECTED_SECTION_ID = "1_0"
    SUBSECTION_NAME = "first_subsection"
    EXPECTED_SUBSECTION_ID = "1_1"
    filter = create_filter(
    f"""{RULE_START}{_INDEX_RULE_NAME}
        {RULE_START}{_SECTION_RULE_NAME} {SECTION_NAME}
        {RULE_START}{_SUBSECTION_RULE_NAME} {SUBSECTION_NAME}""")
    
    text = '\n'.join(index.handle(filter, filter.blocks[0], None))

    assert text.count(_INDEX_HEADER) == 1
    assert text.count(_INDEX_HINT) == 1
    assert text.count(SECTION_NAME) == 3 # the rule, the section and the index
    assert text.count(EXPECTED_SECTION_ID) == 2 # the section and the index
    assert text.count(SUBSECTION_NAME) == 3 # the rule, the section and the index
    assert text.count(EXPECTED_SUBSECTION_ID) == 2 # the section and the index