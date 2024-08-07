import os.path, re
from core import Rule, Line, Block, Filter, ExpectedError

NAME = "import"
_SPLITTER = "->"
_BLOCK_NAME = "name"
_FILTER_EXTENSION = ".filter"

_INCORRECT_RULE_FORMAT_ERROR = "The import '{0}' is formatted incorrectly. Make sure your import rules look like this:\n\n\tfile > path > to > filter -> block_name (optional) -> line_pattern (optional)"
_FILTER_DOES_NOT_EXIST_ERROR = "Could not resolve the import '{0}' to a filter file on your disk."
_BLOCK_NOT_FOUND_ERROR = "The block with name '{0}' was not found."
_LINE_PATTERN_NOT_FOUND_ERROR = "The line pattern '{0}' was not found in block '{1}'."

_EMPTY_PARAMETER_ERROR = "The import '{0}' has no {1}. Make sure to provide one after the arrow."
_BLOCK_NAME_ERROR_TEXT = "block name"
_LINE_PATTERN_ERROR_TEXT = "line pattern"

_CIRCULAR_REFERENCE_ERROR = "The import '{0}' creates a circular reference loop:\n{1}"
_LOOP_STARTS_HERE_ERROR_TEXT = " (LOOP STARTS HERE)"
_LOOP_REPEATS_HERE_ERROR_TEXT = " (LOOP REPEATS HERE)"

class _Params:
    def __init__(self, filepath: str, blockname: str = None, line_pattern: str = None):
        self.filepath = filepath
        self.blockname = blockname
        self.line_pattern = line_pattern

    def __eq__(self, other):
        if not isinstance(other, _Params):
            return False
        equivalent_filepath = os.path.samefile(self.filepath, other.filepath)
        same_block = self.blockname == other.blockname
        same_line_pattern = self.line_pattern == other.line_pattern
        return equivalent_filepath and same_block and same_line_pattern

    def __str__(self):
        string = self.filepath
        string += f" {_SPLITTER} " + self.blockname if self.blockname is not None else ""
        string += f" {_SPLITTER} " + self.line_pattern if self.line_pattern is not None else ""
        return string

_filter_cache: dict[str, Filter] = {}

def handle(filter: Filter, block: Block, _):
    """Handles text import from filter files. Options are ignored."""
    params = _get_initial_params(filter.filepath, block)
    return [ str(line) for line in _get_lines_from_block(block, [ params ], True)]

def _get_initial_params(filepath: str, block: Block):
    name_rules = block.get_rules(_BLOCK_NAME)
    
    if len(name_rules) > 0:
        blockname = name_rules[-1].description.strip()
        return _Params(filepath, blockname)
    
    return _Params(filepath)

def _get_lines_from_filter(filter: Filter, params: list[_Params]) -> list[Line]:
    return [ line
        for block in filter.blocks
        for line in _get_lines_from_block(block, params, True) ]

def _get_lines_from_block(block: Block, params: list[_Params], include_blockstarts: bool) -> list[Line]:
    return [ line
        for block_line in block.lines
        for line in _get_lines_from_line(block_line, params, include_blockstarts) ]

def _get_lines_from_line(line: Line, params: list[_Params], include_blockstarts: bool) -> list[Line]:
    first_line = [ line ] if include_blockstarts or not line.is_block_starter() else []
    return first_line + [ line
        for rule in line.get_rules(NAME)
        for line in _get_lines_from_rule(rule, params) ]

def _get_lines_from_rule(rule: Rule, params: list[_Params]) -> list[Line]:
    new_params = _parse_rule_params(rule, params)

    filter = _get_filter(new_params.filepath)
    if new_params.blockname is None:
        return _get_lines_from_filter(filter, params + [ new_params ])

    block = _get_block(filter, new_params.blockname)
    if new_params.line_pattern is None:
        return _get_lines_from_block(block, params + [ new_params ], False)

    line = _get_line(block, new_params.line_pattern, new_params.filepath)
    return _get_lines_from_line(line, params + [ new_params ], True)

def _parse_rule_params(rule: Rule, previous_params: list[_Params]):
    current_filepath = previous_params[-1].filepath
    
    parts = [ part.strip() for part in rule.description.split(_SPLITTER) ]
    if len(parts) > 3:
        error = _INCORRECT_RULE_FORMAT_ERROR.format(rule.description)
        raise ExpectedError(error, rule.line_number, current_filepath)
    
    filepath = _parse_rule_filepath(current_filepath, parts[0])
    if not os.path.exists(filepath):
        error = _FILTER_DOES_NOT_EXIST_ERROR.format(rule.description)
        raise ExpectedError(error, rule.line_number, current_filepath)

    blockname = parts[1] if len(parts) > 1 else None
    if blockname == "":
        error = _EMPTY_PARAMETER_ERROR.format(rule.description, _BLOCK_NAME_ERROR_TEXT)
        raise ExpectedError(error, rule.line_number, current_filepath)
    
    line_pattern = parts[2] if len(parts) > 2 else None
    if line_pattern == "":
        error = _EMPTY_PARAMETER_ERROR.format(rule.description, _LINE_PATTERN_ERROR_TEXT)
        raise ExpectedError(error, rule.line_number, current_filepath)

    params = _Params(filepath, blockname, line_pattern)
    if any(params == previous for previous in previous_params):
        error = _create_circular_reference_error(rule.description, previous_params, params)
        raise ExpectedError(error, rule.line_number, current_filepath)

    return params

def _get_filter(filepath: str):
    absolute_filepath = os.path.abspath(filepath)

    if absolute_filepath not in _filter_cache:
        _filter_cache[absolute_filepath] = Filter.load(filepath)

    return _filter_cache[absolute_filepath]

def _get_block(filter: Filter, blockname: str):
    for block in filter.blocks:
        if blockname == _get_blockname(block):
            return block
    error = _BLOCK_NOT_FOUND_ERROR.format(blockname)
    raise ExpectedError(error, filepath=filter.filepath)

def _get_line(block: Block, line_pattern: str, filepath: str):
    for line in block.lines:
        if line.contains(line_pattern):
            return line
    blockname = _get_blockname(block)
    error = _LINE_PATTERN_NOT_FOUND_ERROR.format(line_pattern, blockname)
    raise ExpectedError(error, block.line_number, filepath)

def _get_blockname(block: Block):
    name_rules = block.get_rules(_BLOCK_NAME)
    return name_rules[-1].description if len(name_rules) > 0 else None

def _parse_rule_filepath(source_filepath: str, rule_filepath: str):
    if rule_filepath.strip() == "":
        return source_filepath
    
    directory = os.path.dirname(source_filepath)
    directory = re.sub("([\\w\\.])$", "\\1/", directory)

    filepath = re.sub("\\s*>\\s*", "/", rule_filepath)
    filepath = re.sub("\\s*<\\s*", "../", filepath)
    filepath = re.sub("([^\\.^/])\\.", "\\1/.", filepath)
    
    filepath = directory + filepath + _FILTER_EXTENSION
    filepath = os.path.normpath(filepath)
    filepath = re.sub("\\\\", "/", filepath)

    return filepath

def _create_circular_reference_error(rule_description: str, previous_params: list[_Params], looped_params: _Params):
    params_trace = ""
    for params in previous_params:
        params_trace += f"\n\t{params}"
        if looped_params == params:
            params_trace += _LOOP_STARTS_HERE_ERROR_TEXT
    params_trace += f"\n\t{looped_params}{_LOOP_REPEATS_HERE_ERROR_TEXT}"
    return _CIRCULAR_REFERENCE_ERROR.format(rule_description, params_trace)