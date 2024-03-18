from itertools import combinations as Combinations
from core import Block, Line, ExpectedError, Rule

NAME = "choose"

_MULTIPLE_RULES_IN_THE_SAME_BLOCK_ERROR = "Only 1 .choose rule is allowed per block, got {0}."
_RULE_PARAMETER_COUNT_ERROR = "The .choose rule expects exactly 2 parameters in its description, got {0}."
_SET_SIZE_TYPE_ERROR = "The .choose rule expects a number of lines to choose from as the first parameter, got '{0}' instead."
_SET_SIZE_TOO_LARGE_ERROR = "The number of lines to choose from ({0}) exceeds to total number of lines left in the block ({1})."
_SUBSET_SIZE_TYPE_ERROR = "The .choose rule expects a number of lines per choice as the second parameter, got '{0}' instead."
_SUBSET_SIZE_TOO_LARGE_ERROR = "The number of lines per choice ({0}) is greater than the total number of lines to choose from ({1})."

class _Params:
    def __init__(self, start_index: int, set_size: int, subset_size: int):
        self.start_index = start_index
        self.end_index = start_index + set_size
        self.subset_size = subset_size

def handle(_, block: Block, __):
    """Creates new blocks from combinations of lines within a block. Options are ignored."""
    rules = block.get_rules(NAME)
    if len(rules) == 0:
        return block.get_raw_lines()
    
    if len(rules) > 1:
        raise ExpectedError(_MULTIPLE_RULES_IN_THE_SAME_BLOCK_ERROR.format(len(rules)), block.line_number)
    params = _get_params(rules[0], block)

    prefix_lines = block.lines[:params.start_index]
    set_lines = block.lines[params.start_index:params.end_index]
    suffix_lines = block.lines[params.end_index:]

    return _get_combined_raw_lines(prefix_lines, set_lines, suffix_lines, params.subset_size)

def _get_params(rule: Rule, block: Block):
    parts = rule.description.split()
    if len(parts) != 2:
        raise ExpectedError(_RULE_PARAMETER_COUNT_ERROR.format(len(parts)), rule.line_number)
    if not parts[0].isdigit():
        raise ExpectedError(_SET_SIZE_TYPE_ERROR.format(parts[0]), rule.line_number)
    if not parts[1].isdigit():
        raise ExpectedError(_SUBSET_SIZE_TYPE_ERROR.format(parts[1]), rule.line_number)
    
    set_size = int(parts[0])
    subset_size = int(parts[1])
    if subset_size > set_size:
        raise ExpectedError(_SUBSET_SIZE_TOO_LARGE_ERROR.format(subset_size, set_size), rule.line_number)
    
    start_index = rule.line_number - block.line_number + 1
    max_set_size = len(block.lines) - start_index
    if set_size > max_set_size:
        raise ExpectedError(_SET_SIZE_TOO_LARGE_ERROR.format(set_size, max_set_size), rule.line_number)
    
    return _Params(start_index, set_size, subset_size)

def _get_combined_raw_lines(prefix_lines: list[Line], set_lines: list[Line], suffix_lines: list[Line], subset_size: int):
    raw_lines: list[str] = []
    for subset in Combinations(set_lines, subset_size):
        raw_lines += [ str(line) for line in prefix_lines + list(subset) + suffix_lines ]
    return raw_lines