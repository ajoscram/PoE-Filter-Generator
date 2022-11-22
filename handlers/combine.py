from itertools import combinations as Combinations
from typing import Callable

from classes.block import Block
from classes.generator_error import GeneratorError
from classes.line import Line

_NAME = "combine"
_COMBINE_END = "end"

_INCOMPLETE_COMBINE_ERROR = "Your combine is incomplete. Either you provided both rules on the same line, or you're missing the combine's start or end rule."
_MULTIPLE_COMBINE_RULES_IN_SAME_LINE = "You may only provide a single combine rule per line. You've provided {0}."
_FIRST_COMBINE_ARG_ERROR = "The first combine rule expects a positive integer which indicates the size of each combination. You've provided '{0}'."
_LAST_COMBINE_ARG_ERROR = "The last combine rule expects the string literal 'end' to denote the end of the combine. You've provided '{0}'."

def handle(_, block: Block, __):
    """Creates new blocks from combinable lines within a block. Options are ignored."""
        
    if len(block.get_rules(_NAME)) == 0:
        return [ block ]

    first_line = _get_combine_line(block.lines)
    last_line = _get_combine_line(reversed(block.lines))
    _validate_combine_lines(first_line, last_line)

    start_index = first_line.number - block.line_number + 1
    end_index = last_line.number - block.line_number
    size = int(first_line.get_rules(_NAME)[0].description)

    prefix_lines = block.lines[:start_index]
    combine_lines = block.lines[start_index:end_index]
    suffix_lines = block.lines[end_index:]

    return _get_combined_blocks(prefix_lines, combine_lines, suffix_lines, size, block.line_number)

def _get_combine_line(lines: list[Line]):
    return next(line for line in lines if len(line.get_rules(_NAME)) > 0)

def _validate_combine_lines(first_line: Line, last_line: Line):
    if first_line == last_line:
        raise GeneratorError(_INCOMPLETE_COMBINE_ERROR, first_line.number)
    
    first_line_rules = first_line.get_rules(_NAME)
    if len(first_line_rules) > 1:
        raise GeneratorError(_MULTIPLE_COMBINE_RULES_IN_SAME_LINE.format(len(first_line_rules)), first_line.number)

    first_rule_description = first_line_rules[0].description
    if not first_rule_description.isdigit():
        raise GeneratorError(_FIRST_COMBINE_ARG_ERROR.format(first_rule_description), first_line.number)

    last_line_rules = last_line.get_rules(_NAME)
    if len(last_line_rules) > 1:
        raise GeneratorError(_MULTIPLE_COMBINE_RULES_IN_SAME_LINE.format(len(last_line_rules)), last_line.number)
    
    last_rule_description = last_line_rules[0].description
    if last_rule_description != _COMBINE_END:
        raise GeneratorError(_LAST_COMBINE_ARG_ERROR.format(last_rule_description), last_line.number)

    
def _get_combined_blocks(prefix_lines: list[Line], combine_lines: list[Line], suffix_lines: list[Line], size: int, block_line_number: int):
    raw_lines = []
    for combination in [ list(combination) for combination in Combinations(combine_lines, size) ]:
        raw_lines += [ line.text for line in prefix_lines + combination + suffix_lines ]
    return Block.extract(raw_lines, block_line_number)