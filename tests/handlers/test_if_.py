import pytest
from handlers import if_
from handlers.if_ import _EMPTY_DESCRIPTION_ERROR, NAME as IF
from core import ExpectedError, Operand, Delimiter
from test_utilities import create_filter

def test_handle_given_text_is_contained_should_not_comment_out():
    TEXT = "text"
    LINE = f"{TEXT} {Delimiter.RULE_START}{IF} {TEXT}"
    filter = create_filter(LINE)

    lines = if_.handle(filter, filter.blocks[0], None)

    assert len(lines) == 1
    assert LINE == lines[0]

def test_handle_given_if_was_placed_on_blockstarter_should_comment_out_the_block():
    filter = create_filter(
    f"""{Operand.SHOW} {Delimiter.RULE_START}{IF} {Operand.HIDE}
        first line
        second line""")
    
    lines = if_.handle(filter, filter.blocks[0], None)
    
    for line in lines:
        assert line.startswith(Delimiter.COMMENT_START)

def test_handle_given_if_was_placed_on_empty_line_should_comment_out_lines_starting_from_it():
    filter = create_filter(
    f"""{Operand.SHOW}
        {Delimiter.RULE_START}{IF} {Operand.HIDE}
        another line""")
    
    lines = if_.handle(filter, filter.blocks[0], None)

    for line in lines[1:]:
        assert line.startswith(Delimiter.COMMENT_START)

def test_handle_given_if_was_placed_on_non_empty_line_should_comment_out_that_line():
    filter = create_filter(
    f"""{Operand.SHOW}
        first line {Delimiter.RULE_START}{IF} {Operand.HIDE}
        second line""")
    
    lines = if_.handle(filter, filter.blocks[0], None)
    
    assert lines[1].startswith(Delimiter.COMMENT_START)
    assert not lines[2].startswith(Delimiter.COMMENT_START)

def test_given_whitespace_description_on_rule_should_raise():
    filter = create_filter(f"{Delimiter.RULE_START}{IF}    ")

    with pytest.raises(ExpectedError) as error:
        _ = if_.handle(filter, filter.blocks[0], None)
    
    assert error.value.message == _EMPTY_DESCRIPTION_ERROR
    assert error.value.line_number == filter.blocks[0].lines[0].number