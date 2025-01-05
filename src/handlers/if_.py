import re
from enum import IntEnum
from core import Delimiter, Block, Line, ExpectedError

NAME = "if"
_IF_RULE_PATTERN = f"\\{Delimiter.RULE_SEPARATOR}{NAME}[^\\{Delimiter.RULE_SEPARATOR}]*"
_EMPTY_DESCRIPTION_ERROR = "The .if rule description is empty and cannot be validated as a result."

class _RemoveType(IntEnum):
    NONE = 0
    SINGLE = 1
    MUTLI = 2

def handle(_, block: Block, __):
    """Removes lines from blocks if a piece of text is not present within the block.
    Text from `.if` rules is ignored when comparing."""
    block_text = _get_block_text(block)
    for line in block.lines: 
        remove_type = _get_remove_type(line, block_text)
        if remove_type == _RemoveType.SINGLE:
            line.comment_out()
        elif remove_type == _RemoveType.MUTLI:
            block.comment_out(start=line)
            break
    return block.get_raw_lines()

def _get_block_text(block: Block):
    raw_lines = [ re.sub(_IF_RULE_PATTERN, "", raw_line) for raw_line in block.get_raw_lines() ]
    return "\n".join(raw_lines)

def _get_remove_type(line: Line, block_text: str):
    for rule in line.get_rules(NAME):
        if rule.description == "":
            raise ExpectedError(_EMPTY_DESCRIPTION_ERROR, rule.line_number)
        if rule.description in block_text:
            continue
        if line.is_block_starter() or not line.has_filter_info():
            return _RemoveType.MUTLI
        return _RemoveType.SINGLE
    return _RemoveType.NONE
