import re
from core import Delimiter, Line, Block, Filter

NAME = "format"

_RULE_PATTERN = fr"\s*{Delimiter.COMMENT_START}\{Delimiter.RULE_SEPARATOR}.+"

def handle(filter: Filter, block: Block, _):
    """Removes rules, trailing whitespace from lines and extraneous empty lines. Options are ignored."""
    raw_lines = _get_formatted_raw_lines(block.lines)

    if block == filter.blocks[0] and len(raw_lines) > 0 and raw_lines[0] == "":
        raw_lines = raw_lines[1:]

    if block == filter.blocks[-1] and len(raw_lines) > 0 and raw_lines[-1] == "":
        raw_lines = raw_lines[:-1]

    return raw_lines

def _get_formatted_raw_lines(lines: list[Line]) -> list[str]:
    match lines:
        case [ first, second, *tail ] if first.is_empty() and second.is_empty():
            return _get_formatted_raw_lines([ second ] + tail)
        case [ head, *tail ]:
            prefix = _get_raw_line_prefix(head, tail)
            return prefix + _get_formatted_raw_lines(tail)
        case []:
            return []

def _get_raw_line_prefix(head: Line, tail: list[Line]):
    text = str(head).rstrip() if len(head.rules) == 0 else \
        re.sub(_RULE_PATTERN, "", str(head))
    return [ text ] if text.strip() != "" or len(tail) == 0 else []