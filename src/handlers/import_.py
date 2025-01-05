import os.path, re
from enum import StrEnum
from core import Rule, Line, Block, Filter, ExpectedError, Delimiter

NAME = "import"
_NAME_RULE = "name"
_FILTER_EXTENSION = ".filter"

_FILTER_DOES_NOT_EXIST_ERROR = "Could not resolve the import '{0}' to a filter file on your disk."
_BLOCK_NOT_FOUND_ERROR = "The block with name '{0}' was not found."
_LINE_PATTERN_NOT_FOUND_ERROR = "The line pattern '{0}' was not found in block '{1}'."
_ROOT_NOT_FOUND_ERROR = "The root '{0}' in import '{1}' was not received via the handler's options."
_ROOT_FORMAT_ERROR = "The root '{0}' declared via .import's options is formatted incorrectly."

_FORMAT_ERROR = "The import '{0}' could not be parsed because {1}."
_TOO_MANY_SPLITS_ERROR_TEXT = "it contained more than two arrows (`->`)"
_TOO_MANY_ROOTS_ERROR_TEXT = "it contained more than one root separator (`|`)"

_EMPTY_PARAMETER_ERROR = "The import '{0}' has no {1}. Make sure to provide one after the arrow."
_BLOCK_NAME_ERROR_TEXT = "block name"
_LINE_PATTERN_ERROR_TEXT = "line pattern"

_CIRCULAR_REFERENCE_ERROR = "The import '{0}' creates a circular reference loop:\n{1}"
_LOOP_STARTS_HERE_ERROR_TEXT = " (LOOP STARTS HERE)"
_LOOP_REPEATS_HERE_ERROR_TEXT = " (LOOP REPEATS HERE)"

class _Navigation(StrEnum):
    ROOT = "|"
    IN = ">"
    OUT = "<"
    SPLIT = "->"

class _Import:
    def __init__(self, filepath: str, blockname: str = None, line_pattern: str = None):
        self.filepath = filepath
        self.blockname = blockname
        self.line_pattern = line_pattern

    def __eq__(self, other):
        if not isinstance(other, _Import):
            return False
        equivalent_filepath = os.path.samefile(self.filepath, other.filepath)
        same_block = self.blockname == other.blockname
        same_line_pattern = self.line_pattern == other.line_pattern
        return equivalent_filepath and same_block and same_line_pattern

    def __str__(self):
        string = self.filepath
        string += f" {_Navigation.SPLIT} " + self.blockname if self.blockname is not None else ""
        string += f" {_Navigation.SPLIT} " + self.line_pattern if self.line_pattern is not None else ""
        return string

class _Context:
    def __init__(self, roots: dict[str, str], imports: list[_Import]):
        self.roots = roots
        self.imports = imports
    
    def get_current_filepath(self):
        return self.imports[-1].filepath
    
    def get_original_filepath(self):
        return self.imports[0].filepath

    def clone(self, new_import: _Import):
        return _Context(self.roots, self.imports + [ new_import ])

_filter_cache: dict[str, Filter] = {}

def handle(filter: Filter, block: Block, options: list[str]):
    """Handles text import from filter files.
    Absolute paths can be defined via the options."""
    roots = _get_roots(options)
    initial_import = _get_initial_import(filter.filepath, block)
    context = _Context(roots, [ initial_import ])
    return [ str(line) for line in _get_lines_from_block(block, context, True) ]

def _get_initial_import(filepath: str, block: Block):
    name_rules = block.get_rules(_NAME_RULE)
    blockname = name_rules[-1].description.strip() \
        if len(name_rules) > 0 else None
    return _Import(filepath, blockname=blockname)

def _get_roots(options: list[str]):
    if len(options) == 0:
        return {}
    
    root_names_to_values = (_get_root_name_and_value_from_entry(entry)
        for entry in " ".join(options).split(Delimiter.LIST_ENTRY_SEPARATOR))

    return { name: value for name, value in root_names_to_values }

def _get_root_name_and_value_from_entry(entry: str):
    parts = entry.split(Delimiter.PAIR_SEPARATOR)
    if len(parts) != 2:
        raise ExpectedError(_ROOT_FORMAT_ERROR.format(entry))

    return parts[0].strip(), parts[1].strip()

def _get_lines_from_filter(filter: Filter, context: _Context) -> list[Line]:
    return [ line
        for block in filter.blocks
        for line in _get_lines_from_block(block, context, True) ]

def _get_lines_from_block(block: Block, context: _Context, include_blockstarts: bool) -> list[Line]:
    return [ line
        for block_line in block.lines
        for line in _get_lines_from_line(block_line, context, include_blockstarts) ]

def _get_lines_from_line(line: Line, context: _Context, include_blockstarts: bool) -> list[Line]:
    first_line = [ line ] if include_blockstarts or not line.is_block_starter() else []
    return first_line + [ line
        for rule in line.get_rules(NAME)
        for line in _get_lines_from_rule(rule, context) ]

def _get_lines_from_rule(rule: Rule, context: _Context) -> list[Line]:
    new_import = _parse_import(rule, context)

    filter = _get_filter(new_import.filepath)
    if new_import.blockname is None:
        return _get_lines_from_filter(filter, context.clone(new_import))

    block = _get_block(filter, new_import.blockname)
    if new_import.line_pattern is None:
        return _get_lines_from_block(block, context.clone(new_import), False)

    line = _get_line(block, new_import.line_pattern, new_import.filepath)
    return _get_lines_from_line(line, context.clone(new_import), True)

def _parse_import(rule: Rule, context: _Context):
    parts = [ part.strip() for part in rule.description.split(_Navigation.SPLIT) ]
    if len(parts) > 3:
        error = _FORMAT_ERROR.format(rule.description, _TOO_MANY_SPLITS_ERROR_TEXT)
        raise ExpectedError(error, rule.line_number, context.get_current_filepath())

    filepath = _parse_rule_filepath(parts[0], rule, context)
    if not os.path.isfile(filepath):
        error = _FILTER_DOES_NOT_EXIST_ERROR.format(rule.description)
        raise ExpectedError(error, rule.line_number, context.get_current_filepath())

    blockname = parts[1] if len(parts) > 1 else None
    if blockname == "":
        error = _EMPTY_PARAMETER_ERROR.format(rule.description, _BLOCK_NAME_ERROR_TEXT)
        raise ExpectedError(error, rule.line_number, context.get_current_filepath())
    
    line_pattern = parts[2] if len(parts) > 2 else None
    if line_pattern == "":
        error = _EMPTY_PARAMETER_ERROR.format(rule.description, _LINE_PATTERN_ERROR_TEXT)
        raise ExpectedError(error, rule.line_number, context.get_current_filepath())

    import_ = _Import(filepath, blockname, line_pattern)
    if any(import_ == previous for previous in context.imports):
        error = _create_circular_reference_error(rule.description, context.imports, import_)
        raise ExpectedError(error, rule.line_number, context.get_current_filepath())

    return import_

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
        if line_pattern in line:
            return line
    blockname = _get_blockname(block)
    error = _LINE_PATTERN_NOT_FOUND_ERROR.format(line_pattern, blockname)
    raise ExpectedError(error, block.line_number, filepath)

def _get_blockname(block: Block):
    name_rules = block.get_rules(_NAME_RULE)
    return name_rules[-1].description if len(name_rules) > 0 else None

def _parse_rule_filepath(rule_filepath: str, rule: Rule, context: _Context):
    if rule_filepath == "":
        return context.get_current_filepath()
    
    (root, filepath) = _split_root_and_filepath(rule_filepath, rule, context)
    root_dir = _get_root_dir(root, rule, context)
    filepath_suffix = _transform_navigation_to_real_path(filepath)
    return _get_full_filepath(root_dir, filepath_suffix)

def _split_root_and_filepath(rule_filepath: str, rule: Rule, context: _Context):
    parts = [ part.strip() for part in rule_filepath.split(_Navigation.ROOT) ]
    
    if len(parts) > 2:
        error = _FORMAT_ERROR.format(rule.description, _TOO_MANY_ROOTS_ERROR_TEXT)
        raise ExpectedError(error, rule.line_number, context.get_current_filepath())

    return (None, parts[0]) if len(parts) == 1 else (parts[0], parts[1])

def _get_root_dir(root: str | None, rule: Rule, context: _Context):
    match root:
        case None:
            root_dir = os.path.dirname(context.get_current_filepath())
        case "":
            root_dir = os.path.dirname(context.get_original_filepath())
        case _ if root not in context.roots:
            error = _ROOT_NOT_FOUND_ERROR.format(root, rule.description)
            raise ExpectedError(error, rule.line_number, context.get_current_filepath())
        case _:
            path_prefix = os.path.dirname(context.get_original_filepath())
            path_suffix = _transform_navigation_to_real_path(context.roots[root])
            root_dir = os.path.join(path_prefix, path_suffix)

    return re.sub("([\\w\\.])$", "\\1/", root_dir)

def _transform_navigation_to_real_path(navigation_path: str):
    translated_path = re.sub(f"\\s*{_Navigation.IN}\\s*", "/", navigation_path)
    translated_path = re.sub(f"\\s*{_Navigation.OUT}\\s*", "../", translated_path)
    return re.sub("([^\\.^/])\\.", "\\1/.", translated_path)

def _get_full_filepath(root_dir: str, filepath_suffix: str):
    filepath = root_dir + filepath_suffix + _FILTER_EXTENSION
    filepath = os.path.normpath(filepath)
    return re.sub("\\\\", "/", filepath)

def _create_circular_reference_error(rule_description: str, previous_imports: list[_Import], looped_import: _Import):
    import_trace = ""
    for import_ in previous_imports:
        import_trace += f"\n\t{import_}"
        if looped_import == import_:
            import_trace += _LOOP_STARTS_HERE_ERROR_TEXT
    import_trace += f"\n\t{looped_import}{_LOOP_REPEATS_HERE_ERROR_TEXT}"
    return _CIRCULAR_REFERENCE_ERROR.format(rule_description, import_trace)