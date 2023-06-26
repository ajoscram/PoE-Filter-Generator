import re
from enum import Enum
from core import Block, Line, GeneratorError
from core.constants import RULE_SEPARATOR

NAME = "if"
_IF_RULE_PATTERN = f"\\{RULE_SEPARATOR}{NAME}[^\\{RULE_SEPARATOR}]*"
_EMPTY_DESCRIPTION_ERROR = "The .if rule description is empty and cannot be validated as a result."

class _RemoveType(Enum):
    NONE = 0,
    SINGLE = 1,
    MUTLI = 2,

def handle(_, block: Block, __):
    """Removes lines from blocks if a piece of text is not present within the block.
    Text from `.if` rules is ignored when comparing."""
    block_text = _get_block_text(block)
    for line in block.lines: 
        remove_type = _get_remove_type(line, block_text)
        if remove_type == _RemoveType.SINGLE:
            line.comment_out()
        elif remove_type == _RemoveType.MUTLI:
            _comment_out_starting_from_line(block, line)
            break
    
    return block.get_raw_lines()

def _get_block_text(block: Block):
    raw_lines = [ re.sub(_IF_RULE_PATTERN, "", str(line)) for line in block.lines ]
    return "\n".join(raw_lines)

def _get_remove_type(line: Line, block_text: str):
    for rule in line.get_rules(NAME):
        if len(rule.description) == 0:
            raise GeneratorError(_EMPTY_DESCRIPTION_ERROR, rule.line_number)
        if rule.description in block_text:
            continue
        if line.is_block_starter() or line.is_empty(exclude_comments=True):
            return _RemoveType.MUTLI
        return _RemoveType.SINGLE
    return _RemoveType.NONE

def _comment_out_starting_from_line(block: Block, line: Line):
    line_index = line.number - block.line_number
    for line in block.lines[line_index:]:
        line.comment_out()
