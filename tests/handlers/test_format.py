from handlers import format, Context
from core import Operand, Delimiter
from test_utilities import create_filter

def test_handle_given_item_filter_lines_with_rules_should_remove_the_rules_but_keep_the_line():
    RULE_TEXT = f"{Delimiter.RULE_START}rule {Delimiter.RULE_SEPARATOR}other_rule"
    filter = create_filter(f"{Operand.SHOW} {RULE_TEXT}")

    lines = format.handle(filter.blocks[0], Context(filter, None))

    assert RULE_TEXT not in lines[0]

def test_handle_given_line_that_only_contains_rules_should_remove_the_line():
    RULE_TEXT = f"{Delimiter.RULE_START}rule"
    filter = create_filter(f"{Operand.SHOW}\n{RULE_TEXT}")

    lines = format.handle(filter.blocks[0], Context(filter, None))

    assert len(lines) == 1
    assert lines[0] == Operand.SHOW

def test_handle_given_lines_with_trailing_whitespace_should_remove_it():
    WHITESPACE = " "
    FILTER = create_filter(f"{Operand.SHOW}{WHITESPACE}")

    lines = format.handle(FILTER.blocks[0], Context(FILTER, None))

    assert WHITESPACE not in lines[0]

def test_handle_given_linebreaks_before_and_after_the_filter_contents_should_remove_them():
    filter = create_filter(f"\n{Operand.SHOW}\n{Operand.HIDE}\n\n")

    lines = [ line
        for block in filter.blocks
        for line in format.handle(block, Context(filter, None)) ]

    assert len(lines) == 3

def test_handle_given_duplicate_linebreaks_in_a_row_should_reduce_them_to_one():
    filter = create_filter(f"{Operand.SHOW}\n\n\n{Operand.SHOW}")

    lines = [ line
        for block in filter.blocks
        for line in format.handle(block, Context(filter, None)) ]

    assert len(lines) == 3

def test_handle_given_rule_after_empty_line_should_remove_both():
    filter = create_filter(f"{Operand.SHOW}\n\n{Delimiter.RULE_START}rule")

    lines = format.handle(filter.blocks[0], Context(filter, None))

    assert len(lines) == 1
    assert lines[0] == Operand.SHOW

def test_handle_given_line_with_comments_should_preserve_them():
    filter = create_filter(f"{Operand.SHOW}\n{Delimiter.COMMENT_START} a comment")

    lines = format.handle(filter.blocks[0], Context(filter, None))

    assert len(lines) == 2