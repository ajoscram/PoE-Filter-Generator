import re

from classes.block import Block
from classes.filter import Filter
from classes.rule import COMMENT_START, RULE_START

def handle(filter: Filter, block: Block, __):
    """Removes rules, empty lines and trailing whitespace. Appends a single empty line at the end of each block."""
    lines = [ _format(line.text) for line in block.lines ]
    lines = [ line for line in lines if line.strip() != "" ]
    if block != filter.blocks[-1]:
        lines += [ "\n" ]
    return Block.extract(lines, block.line_number)

def _format(line: str):
    if not COMMENT_START in line.split(RULE_START)[0]:
        line = re.sub("#\..+", "", line)
    return line.rstrip()