import re
from typing import Iterator
from core import Delimiter, Line, Block
from .context import Context

NAME = "format"

_RULE_PATTERN = fr"\s*{Delimiter.COMMENT_START}\{Delimiter.RULE_SEPARATOR}.+"
_INDENT = " " * 4

def handle(block: Block, context: Context):
    """Removes rules, trailing whitespace from lines and extraneous empty lines. Options are ignored."""
    lines = _get_valid_lines(block.lines)
    raw_lines = [ _get_formatted_raw_line(line) for line in lines ]

    if block != context.filter.blocks[-1]:
        raw_lines += [ "\n" ]

    if block == context.filter.blocks[0] and len(raw_lines) > 0 and raw_lines[0].strip() == "":
        raw_lines = raw_lines[1:]

    return raw_lines

def _get_valid_lines(lines: list[Line]) -> Iterator[Line]:
    for index, line in enumerate(lines):

        has_format_rules = len(line.get_rules(NAME)) > 0
        if has_format_rules and not line.has_filter_info():
            break
        if has_format_rules:
            continue

        line_is_removable = not (line.has_filter_info() or line.has_comment())
        if line_is_removable and line != lines[-1] and not lines[index + 1].has_comment():
            continue
        if line_is_removable and line == lines[-1]:
            continue

        yield line

def _get_formatted_raw_line(line: Line):
    raw_line = str(line).strip()

    if line.has_rules():
        raw_line = re.sub(_RULE_PATTERN, "", raw_line)

    if line.has_filter_info() and not line.is_block_starter():
        return _INDENT + raw_line

    return raw_line