import pytest
from test_utilities import create_filter
from core import Block, Delimiter, Operand, ExpectedError
from handlers.multi import NAME, _END_PARAM, _PREMATURE_END_PARAM_ERROR
from handlers import multi, Context

_FIRST_LINE = "first"
_SECOND_LINE = "second"

@pytest.mark.parametrize("text", [
    f"{Operand.SHOW}\n{Delimiter.RULE_START}{NAME}\n{_FIRST_LINE}",
    f"{Operand.SHOW}\n{_FIRST_LINE}"])
def test_handle_given_an_idempotent_number_of_multi_rules_should_return_the_same_block(text: str):
    filter = create_filter(text)
    
    lines = multi.handle(filter.blocks[0], Context(filter, []))
    blocks = Block.extract(lines)

    assert len(blocks) == 1
    assert str(blocks[0]) == text

def test_handle_given_multiple_multi_rules_should_create_a_block_for_each():
    filter = create_filter(
    f"""{Operand.SHOW}
        {_FIRST_LINE} {Delimiter.RULE_START}{NAME}
        {_SECOND_LINE} {Delimiter.RULE_START}{NAME}""")
    
    lines = multi.handle(filter.blocks[0], Context(filter, []))
    blocks = Block.extract(lines)

    assert len(blocks) == 2
    assert _FIRST_LINE in str(blocks[0])
    assert _FIRST_LINE not in str(blocks[1])    
    assert _SECOND_LINE not in str(blocks[0])
    assert _SECOND_LINE in str(blocks[1])

def test_handle_given_end_param_should_include_the_last_multi_in_the_last_block():
    filter = create_filter(
    f"""{Operand.SHOW}
        {_FIRST_LINE} {Delimiter.RULE_START}{NAME}
        {Delimiter.RULE_START}{NAME} {_END_PARAM}""")
    
    lines = multi.handle(filter.blocks[0], Context(filter, []))
    blocks = Block.extract(lines)

    assert len(blocks) == 1
    assert f"{Delimiter.RULE_START}{NAME} {_END_PARAM}" in str(blocks[0])

def test_handle_given_end_param_should_put_suffix_lines_on_all_blocks():
    SUFFIX_LINE = "suffix"
    filter = create_filter(
    f"""{Operand.SHOW}
        {_FIRST_LINE} {Delimiter.RULE_START}{NAME}
        {_SECOND_LINE} {Delimiter.RULE_START}{NAME}
        {SUFFIX_LINE} {Delimiter.RULE_START}{NAME} {_END_PARAM}""")
    
    lines = multi.handle(filter.blocks[0], Context(filter, []))
    blocks = Block.extract(lines)

    assert len(blocks) == 2
    assert SUFFIX_LINE in str(blocks[0])
    assert SUFFIX_LINE in str(blocks[1])

def test_handle_given_premature_end_param_should_raise():
    filter = create_filter(
    f"""{Operand.SHOW}
        {_FIRST_LINE} {Delimiter.RULE_START}{NAME} {_END_PARAM}
        {_SECOND_LINE} {Delimiter.RULE_START}{NAME}""")
    
    with pytest.raises(ExpectedError) as error:
        multi.handle(filter.blocks[0], Context(filter, []))

    assert error.value.message == _PREMATURE_END_PARAM_ERROR
    assert error.value.line_number == 2
    assert error.value.filepath == filter.filepath