import os.path, re

import classes.block
from classes.filter import Filter
from classes.generator_error import GeneratorError
from classes.rule import Rule
from classes.block import Block

_NAME = "import"
_SPLITTER = "->"
_BLOCK_NAME = "name"

_INCORRECT_RULE_FORMAT_ERROR = "The import '{0}' is formatted incorrectly. Make sure your import rules look like this:\n\n\tfile > path > to > filter -> block_name (optional) -> line_pattern (optional)"
_FILTER_DOES_NOT_EXIST_ERROR = "Could not resolve the import '{0}' to a filter file on your disk."
_CIRCULAR_REFERENCE_ERROR = "The import '{0}' creates a circular reference loop."
_EMPTY_PARAMETER_ERROR = "The import '{0}' has no {1}. Make sure to provide one after the arrow."
_BLOCK_NOT_FOUND_ERROR = "The block with name '{0}' was not found."
_LINE_PATTERN_NOT_FOUND = "The line pattern '{0}' was not found in block '{1}'."

class _Params:
    def __init__(self, filepath: str, blockname: str = None, line_pattern: str = None):
        self.filepath = filepath
        self.blockname = blockname
        self.line_pattern = line_pattern
    
    def cycle_with(self, other):
        equivalent_filepaths = os.path.samefile(self.filepath, other.filepath)
        equivalent_blocks = self._check_equal_or_none(self.blockname, other.blockname)
        equivalent_line_patterns = self._check_equal_or_none(self.line_pattern, other.line_pattern)
        return equivalent_filepaths and equivalent_blocks and equivalent_line_patterns
    
    def _check_equal_or_none(first: str, second: str):
        equal = first == second
        either_none = first == None or second == None
        return equal or either_none

_filter_cache: dict[str, Filter] = {}

def handle(filter: Filter, block: Block, _):
    """Handles appends of lines to blocks. Options are ignored."""
    params = _get_initial_params(filter.filepath, block)
    lines = _get_lines_from_block(block, params)
    return Block.extract(lines, block.line_number)

def _get_initial_params(filepath: str, block: Block):
    name_rules = block.get_rules(_BLOCK_NAME)
    if len(name_rules) > 0:
        blockname = name_rules[-1].description.strip()
        return [ _Params(filepath, blockname) ]
    else:
        return [ _Params(filepath) ]

def _get_lines_from_filter(filter: Filter, previous_params: list[_Params]):
    lines = []
    for block in filter.blocks:
        lines += _get_lines_from_block(block, previous_params)
    return lines

def _get_lines_from_block(block: Block, previous_params: list[_Params]):
    lines = []
    line_offset = 0
    rules = block.get_rules(_NAME)
    for line in block.lines:
        line_number = block.line_number + line_offset
        rules_in_line = [ rule for rule in rules if rule.line_number == line_number ]
        lines += _get_lines_from_line(line, rules_in_line)
        line_offset += 1
    return lines

    for rule in block.get_rules(_NAME):
        imported_lines = _get_imported_lines(rule, previous_params)
        lines += block.lines[line_offset : rule.line_number - block.line_number + 1]
        lines += [ line for line in imported_lines if _line_is_valid(line) ]
        line_offset = rule.line_number - block.line_number + 1
    return lines + block.lines[line_offset :]

def _get_lines_from_line(line: str, rules: list[Rule]):

    pass

def _get_imported_lines(rule: Rule, previous_params: list[_Params]):
    params = _parse_rule_params(rule, previous_params)

    filter = _get_filter(params.filepath)
    if params.blockname == None:
        return _get_lines_from_filter(filter, previous_params + [ params ])

    block = _get_block(filter, params.blockname)
    if params.line_pattern == None:
        return _get_lines_from_block(filter, previous_params + [ params ])

    line = _get_line(block, params.line_pattern, params.filepath)
    return _get_lines_from_line(line, )
    #return _get_lines(block, filter.filepath, previous_params + [ params ])

def _parse_rule_params(rule: Rule, previous_params: list[_Params]):
    current_filepath = previous_params[-1].filepath
    
    parts = rule.description.split(_SPLITTER)
    if len(parts) > 3:
        error = _INCORRECT_RULE_FORMAT_ERROR.format(rule.description)
        raise GeneratorError(error, rule.line_number, current_filepath)
    
    filepath = _parse_rule_filepath(current_filepath, parts[0].strip())
    if not os.path.exists(filepath):
        error = _FILTER_DOES_NOT_EXIST_ERROR.format(rule.description)
        raise GeneratorError(error, rule.line_number, current_filepath)

    blockname = parts[1].strip() if len(parts) > 1 else None
    if blockname == "":
        error = _EMPTY_PARAMETER_ERROR.format(rule.description, "block name")
        raise GeneratorError(error, rule.line_number, current_filepath)
    
    line_pattern = parts[2].strip() if len(parts) > 2 else None
    if line_pattern == "":
        error = _EMPTY_PARAMETER_ERROR.format(rule.description, "line pattern")
        raise GeneratorError(error, rule.line_number, current_filepath)

    params = _Params(filepath, blockname, line_pattern)
    if any(params.cycle_with(previous) for previous in previous_params):
        error = _CIRCULAR_REFERENCE_ERROR.format(rule.description)
        raise GeneratorError(error, rule.line_number, current_filepath)

    return params

def _get_filter(filepath: str):
    absolute_filepath = os.path.abspath(filepath)

    if absolute_filepath not in _filter_cache:
        _filter_cache[absolute_filepath] = Filter(filepath)

    return _filter_cache[absolute_filepath]

def _get_block(filter: Filter, blockname: str):
    for block in filter.blocks:
        if blockname == _get_blockname(block):
            return block
    error = _BLOCK_NOT_FOUND_ERROR.format(blockname)
    raise GeneratorError(error, filepath=filter.filepath)

def _get_line(block: Block, line_pattern: str, filepath: str):
    for line in block.lines:
        if line_pattern in line:
            return line
    blockname = _get_blockname(block)
    error = _LINE_PATTERN_NOT_FOUND.format(line_pattern, blockname)
    raise GeneratorError(error, block.line_number, filepath)

def _get_blockname(block: Block):
    name_rules = block.get_rules(_BLOCK_NAME)
    return name_rules[-1].description.strip() if len(name_rules) > 0 else None

def _line_is_valid(line: str):
    show_start = line.lstrip().startswith(classes.block._SHOW)
    hide_start = line.lstrip().startswith(classes.block._HIDE)
    return not show_start and not hide_start

def _parse_rule_filepath(source_filepath: str, rule_filepath: str):
    directory = os.path.dirname(source_filepath)
    directory = re.sub("([\w\.])$", "\\1/", directory)

    rule_filepath = re.sub("\s*>\s*", "/", rule_filepath)
    rule_filepath = re.sub("\s*<\s*", "../", rule_filepath)
    rule_filepath = re.sub("([^\.])\.", "\\1/.", rule_filepath)

    new_filepath = directory + rule_filepath + ".filter"
    new_filepath = re.sub("/[^/]*/\.\.", "", new_filepath)

    return new_filepath