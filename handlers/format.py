import re

from classes.block import Block
from classes.filter import Filter
from classes.rule import COMMENT_START, RULE_START

def handle(filter: Filter, block: Block, _):
    """Removes rules, empty lines and trailing whitespace. Appends a single empty line at the end of each block."""
    raw_lines = [ _format(line.text) for line in block.lines ]
    raw_lines = [ raw_line for raw_line in raw_lines if raw_line.strip() != "" ]
    if block != filter.blocks[-1]:
        raw_lines += [ "\n" ]
    return Block.extract(raw_lines, block.line_number)

def _format(raw_line: str):
    if not COMMENT_START in raw_line.split(RULE_START)[0]:
        raw_line = re.sub("#\..+", "", raw_line)
    return raw_line.rstrip()