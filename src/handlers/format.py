import re
from core import Delimiter, Line, Block, Filter

NAME = "format"

_RULE_PATTERN = fr"\s*{Delimiter.COMMENT_START}\{Delimiter.RULE_SEPARATOR}.+"

def handle(filter: Filter, block: Block, _):
    """Removes rules, trailing whitespace from lines and extraneous empty lines. Options are ignored."""
    raw_lines = _get_formatted_raw_lines(block.lines)
    raw_lines += [ "\n" ] if block != filter.blocks[-1] else []

    if block == filter.blocks[0] and len(raw_lines) > 0 and raw_lines[0].strip() == "":
        raw_lines = raw_lines[1:]

    return raw_lines

def _get_formatted_raw_lines(lines: list[Line]) -> list[str]:
    match lines:
        case [ first, second, *rest ] if first.is_empty() and (second.has_filter_info() or second.is_empty()):
            return _get_formatted_raw_lines([ second ] + rest)

        case [ first, second, *rest ] if first.is_empty() and not (second.has_filter_info() or second.has_comment()):
            return _get_formatted_raw_lines([ first ] + rest)

        case [ first, *rest ] if first.has_rules() and not first.has_filter_info():
            return _get_formatted_raw_lines(rest)

        case [ first, *rest ] if first.has_rules() and first.has_filter_info():
            text = re.sub(_RULE_PATTERN, "", str(first))
            line = Line(text, first.number)
            return _get_formatted_raw_lines([ line ] + rest)
        
        case [ first, *rest ] if first.has_filter_info():
            text = " " * (0 if first.is_block_starter() else 4) + str(first).strip()
            return [ text ] + _get_formatted_raw_lines(rest)
        
        case [ first ] if first.is_empty():
            return []

        case [ first, *rest ]:
            return [ str(first).rstrip() ] + _get_formatted_raw_lines(rest)

        case []:
            return []