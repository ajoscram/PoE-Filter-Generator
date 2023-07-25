from handlers import format
from core import HIDE, RULE_START, SHOW
from test_utilities import create_filter

def test_handle_given_lines_with_rules_should_remove_them():
    RULE_TEXT = f"{RULE_START}rule .other_rule"
    FILTER = create_filter(f"{SHOW} {RULE_TEXT}")

    lines = format.handle(FILTER, FILTER.blocks[0], None)

    assert RULE_TEXT not in lines[0]

def test_handle_given_lines_with_trailing_whitespace_should_remove_it():
    WHITESPACE = " "
    FILTER = create_filter(f"{SHOW}{WHITESPACE}")

    lines = format.handle(FILTER, FILTER.blocks[0], None)

    assert WHITESPACE not in lines[0]

def test_handle_given_linebreaks_before_and_after_the_filter_contents_should_remove_them():
    FILTER = create_filter(f"\n{SHOW}\n{HIDE}\n\n")

    lines = [ line for block in FILTER.blocks for line in format.handle(FILTER, block, None) ]

    assert len(lines) == 2

def test_handle_given_duplicate_linebreaks_in_a_row_should_reduce_them_to_one():
    FILTER = create_filter(f"{SHOW}\n\n\n{SHOW}")

    lines = [ line for block in FILTER.blocks for line in format.handle(FILTER, block, None) ]

    assert len(lines) == 3