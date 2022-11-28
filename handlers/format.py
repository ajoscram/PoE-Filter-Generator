import re

from classes.block import Block
from classes.filter import Filter
from classes.line import Line

def handle(filter: Filter, block: Block, _):
    """Removes rules, trailing whitespace from lines and extraneous empty lines."""
    raw_lines = [ _format(line) for line in block.lines ]
    raw_lines = _remove_duplicate_empty_lines(raw_lines)

    if block == filter.blocks[0] and raw_lines[0] == "":
        raw_lines = raw_lines[1:]

    if block == filter.blocks[-1] and raw_lines[-1] == "":
        raw_lines = raw_lines[:-1]

    return Block.extract(raw_lines, block.line_number)

def _format(line: Line):
    text = line.text
    if len(line.rules) > 0:
        text = re.sub("#\..+", "", text)
    return text.rstrip()

def _remove_duplicate_empty_lines(raw_lines: list[str]):
    
    if len(raw_lines) < 2:
        return raw_lines

    new_raw_lines = []
    for i in range(len(raw_lines)):
        is_last_line = i == len(raw_lines) - 1
        if is_last_line or raw_lines[i] != "" or raw_lines[i+1] != "":
            new_raw_lines += [ raw_lines[i] ]

    return new_raw_lines