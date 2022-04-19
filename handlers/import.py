import os.path, re

from classes.generator_error import GeneratorError
from classes.filter import Filter
from classes.block import Block
from classes.line import Line
from classes.rule import Rule

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
    
    def _check_equal_or_none(self, first: str, second: str):
        equal = first == second
        either_none = first == None or second == None
        return equal or either_none

_filter_cache: dict[str, Filter] = {}

def handle(filter: Filter, block: Block, _):
    """Handles appends of lines to blocks. Options are ignored."""
    params = _get_initial_params(filter.filepath, block)
    lines = _get_lines_from_block(block, params, True)
    return _get_formatted_blocks(lines, block.line_number)

def _get_initial_params(filepath: str, block: Block):
    name_rules = block.get_rules(_BLOCK_NAME)
    if len(name_rules) > 0:
        blockname = name_rules[-1].description.strip()
        return [ _Params(filepath, blockname) ]
    else:
        return [ _Params(filepath) ]

def _get_formatted_blocks(lines: list[Line], line_number: int):
    raw_lines = [ line.text for line in lines if not line.is_empty() ]
    blocks = Block.extract(raw_lines, line_number)
    for block in blocks:
        block.append("\n")
    return blocks

def _get_lines_from_filter(filter: Filter, params: list[_Params]) -> list[Line]:
    lines = []
    for block in filter.blocks:
        lines += _get_lines_from_block(block, params, True)
    return lines

def _get_lines_from_block(block: Block, params: list[_Params], include_blockstarts: bool) -> list[Line]:
    lines = []
    for line in block.lines:
        lines += _get_lines_from_line(line, params, include_blockstarts)
    return lines

def _get_lines_from_line(line: Line, params: list[_Params], include_blockstarts: bool):
    lines = [ line ] if not line.is_block_starter() or include_blockstarts else []
    for rule in line.get_rules(_NAME):
        lines += _get_lines_from_rule(rule, params)
    return lines

def _get_lines_from_rule(rule: Rule, params: list[_Params]):
    new_params = _parse_rule_params(rule, params)

    filter = _get_filter(new_params.filepath)
    if new_params.blockname == None:
        return _get_lines_from_filter(filter, params + [ new_params ])

    block = _get_block(filter, new_params.blockname)
    if new_params.line_pattern == None:
        return _get_lines_from_block(block, params + [ new_params ], False)

    line = _get_line(block, new_params.line_pattern, new_params.filepath)
    return _get_lines_from_line(line, params + [ new_params ], True)

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
        if line.contains(line_pattern) or line.contains_in_comment(line_pattern):
            return line
    blockname = _get_blockname(block)
    error = _LINE_PATTERN_NOT_FOUND.format(line_pattern, blockname)
    raise GeneratorError(error, block.line_number, filepath)

def _get_blockname(block: Block):
    name_rules = block.get_rules(_BLOCK_NAME)
    return name_rules[-1].description.strip() if len(name_rules) > 0 else None

def _parse_rule_filepath(source_filepath: str, rule_filepath: str):
    if rule_filepath.strip() == "":
        return source_filepath
    
    directory = os.path.dirname(source_filepath)
    directory = re.sub("([\w\.])$", "\\1/", directory)

    rule_filepath = re.sub("\s*>\s*", "/", rule_filepath)
    rule_filepath = re.sub("\s*<\s*", "../", rule_filepath)
    rule_filepath = re.sub("([^\.])\.", "\\1/.", rule_filepath)
    rule_filepath = re.sub("\.\.//\.\.", "../..", rule_filepath)
    
    new_filepath = directory + rule_filepath + ".filter"

    return os.path.normpath(new_filepath)