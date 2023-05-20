import re
from core import Line, Block, Filter, COMMENT_START, RULE_SEPARATOR

_RULE_PATTERN = F"{COMMENT_START}\{RULE_SEPARATOR}.+"

def handle(filter: Filter, block: Block, _):
    """Removes rules, trailing whitespace from lines and extraneous empty lines. Options are ignored."""
    raw_lines = _get_formatted_raw_lines(block.lines)
    raw_lines = _remove_duplicate_empty_lines(raw_lines)

    if block == filter.blocks[0] and len(raw_lines) > 0 and raw_lines[0] == "":
        raw_lines = raw_lines[1:]
    
    if block == filter.blocks[-1] and len(raw_lines) > 0 and raw_lines[-1] == "":
        raw_lines = raw_lines[:-1]

    return raw_lines

def _get_formatted_raw_lines(lines: list[Line]):
    raw_lines = []
    for line in lines:
        raw_line = re.sub(_RULE_PATTERN, "", str(line)) if len(line.rules) > 0 else str(line).rstrip()
        if len(line.rules) == 0 or raw_line.strip() != "":
            raw_lines += [ raw_line ]
    return raw_lines

def _remove_duplicate_empty_lines(raw_lines: list[str]):
    if len(raw_lines) < 2:
        return raw_lines

    new_raw_lines = []
    for i in range(len(raw_lines)):
        is_last_line = i == len(raw_lines) - 1
        if is_last_line or raw_lines[i] != "" or raw_lines[i+1] != "":
            new_raw_lines += [ raw_lines[i] ]

    return new_raw_lines