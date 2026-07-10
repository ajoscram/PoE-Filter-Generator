import os.path, re, utils
from abc import ABC
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Generator
from core import Rule, Line, Block, Filter, ExpectedError
from .context import Context

NAME = "import"
_NAME_RULE = "name"
_FILTER_EXTENSION = ".filter"

_FILTER_DOES_NOT_EXIST_ERROR = "Could not resolve the import '{0}' to a filter file on your disk."
_BLOCK_NOT_FOUND_ERROR = "The block with name '{0}' was not found."
_ROOT_NOT_FOUND_ERROR = "The root '{0}' in import '{1}' was not received via the handler's options."

_SEGMENT_ERROR_PRELUDE = "The import '{0}' is formatted incorrectly. "
_SEGMENT_FORMAT_ERROR = _SEGMENT_ERROR_PRELUDE + "It's {1} '{2}' contains a {3} separator (`{4}`)."
_EMPTY_SEGMENT_ERROR = _SEGMENT_ERROR_PRELUDE + "It's {1} is empty."

_CIRCULAR_REFERENCE_ERROR = "The import '{0}' creates a circular reference loop:\n{1}"
_LOOP_STARTS_HERE_ERROR_TEXT = " (LOOP STARTS HERE)"
_LOOP_REPEATS_HERE_ERROR_TEXT = " (LOOP REPEATS HERE)"

class _Navigation(StrEnum):
    IN = ">"
    OUT = "<"

class _Splitter(StrEnum):
    ROOT = "|"
    BLOCKNAME = "->"
    TEMPLATE = "{"

@dataclass
class _Import:
    filepath: str
    blockname: str | None
    templates: dict[str, str] = field(default_factory=dict[str, str])

    def __eq__(self, other):
        if not isinstance(other, _Import):
            return False

        equivalent_filepath = os.path.samefile(self.filepath, other.filepath)
        same_block = self.blockname == other.blockname
        return equivalent_filepath and same_block

    def __str__(self):
        string = self.filepath
        string += f" {_Splitter.BLOCKNAME} " + self.blockname if self.blockname is not None else ""
        return string

@dataclass
class ImportContext(Context):
    """Represents a Context used by the .import handler"""
    roots: dict[str, str] = None
    cache: dict[str, Filter] = field(default_factory=dict[str, Filter])
    imports: list[_Import] = field(default_factory=list[_Import])

    def __post_init__(self):
        if self.roots is None:
            self.roots = { name: value
                for name, value in utils.parse_key_value_list(" ".join(self.options)) }
    
    @property
    def current_filepath(self):
        return self.imports[-1].filepath
    
    @property
    def original_filepath(self):
        return self.imports[0].filepath
    
    def clone(self, new_import: _Import):
        return ImportContext(
            self.filter,
            self.options,
            self.roots,
            self.cache,
            self.imports + [new_import])

@dataclass
class _ImportSegment(ABC):
    name: str
    regex: str
    allows_empty: bool = False

@dataclass
class _NamedImportSegment(_ImportSegment):
    def __init__(self, name: str , regex: str):
        super().__init__(name, regex.format(name=name), allows_empty=True)

class _SplitterImportSegment(_ImportSegment):
    def __init__(self, splitter: _Splitter, regex: str, allows_empty: bool = False):
        super().__init__(
            splitter.name.lower(),
            regex.format(name=splitter.name.lower(), splitter=splitter.value),
            allows_empty)

_ROOT_SEGMENT = _SplitterImportSegment(_Splitter.ROOT, r"(?:(?P<{name}>.*?)\s*\{splitter})", allows_empty=True)
_NAVIGATION_SEGMENT = _NamedImportSegment("navigation", r"(?P<{name}>.*?)")
_BLOCKNAME_SEGMENT = _SplitterImportSegment(_Splitter.BLOCKNAME, r"(?:{splitter}\s*(?P<{name}>.*?))")
_TEMPLATE_SEGMENT = _SplitterImportSegment(_Splitter.TEMPLATE, r"(?:{splitter}\s*(?P<{name}>.*?))")
_IMPORT_REGEX = fr"^\s*{_ROOT_SEGMENT.regex}?\s*{_NAVIGATION_SEGMENT.regex}\s*{_BLOCKNAME_SEGMENT.regex}?\s*{_TEMPLATE_SEGMENT.regex}?\s*$"

def handle(block: Block, context: ImportContext):
    """Handles text import from filter files.
    Absolute paths can be defined via the options."""
    initial_import = _get_initial_import(context.filter.filepath, block)
    context = context.clone(initial_import)
    return [ str(line) for line in _get_lines_from_block(block, context, True) ]

def _get_initial_import(filepath: str, block: Block):
    name_rules = block.get_rules(_NAME_RULE)
    blockname = name_rules[-1].description.strip() \
        if len(name_rules) > 0 else None
    return _Import(filepath, blockname)

def _get_lines_from_filter(filter: Filter, context: ImportContext) -> Generator[Line, None, None]:
    return (line
        for block in filter.blocks
        for line in _get_lines_from_block(block, context, True))

def _get_lines_from_block(block: Block, context: ImportContext, include_blockstarts: bool) -> Generator[Line, None, None]:
    return (line
        for block_line in block.lines
        for line in _get_lines_from_line(block_line, context, include_blockstarts))

def _get_lines_from_line(line: Line, context: ImportContext, include_blockstarts: bool) -> Generator[Line, None, None]:
    if include_blockstarts or not line.is_block_starter():
        yield line # TODO: account for templating

    for rule in line.get_rules(NAME):
        for line in _get_lines_from_rule(rule, context):
            yield line

def _get_lines_from_rule(rule: Rule, context: ImportContext) -> Generator[Line, None, None]:
    new_import = _parse_import(rule, context)

    filter = _get_filter(new_import.filepath, context)
    if new_import.blockname is None:
        return _get_lines_from_filter(filter, context.clone(new_import))

    block = _get_block(filter, new_import.blockname)
    return _get_lines_from_block(block, context.clone(new_import), False)

def _parse_import(rule: Rule, context: ImportContext):
    match = re.search(_IMPORT_REGEX, rule.description)
    root = _get_segment_text(_ROOT_SEGMENT, match, rule, context)
    navigation = _get_segment_text(_NAVIGATION_SEGMENT, match, rule, context)
    blockname = _get_segment_text(_BLOCKNAME_SEGMENT, match, rule, context)
    templates_text = _get_segment_text(_TEMPLATE_SEGMENT, match, rule, context)
    
    templates = {} if templates_text is None else \
        { key: value for key, value in utils.parse_key_value_list(templates_text, rule.line_number) } 
    
    filepath = _parse_rule_filepath(root, navigation, rule, context)
    if not os.path.isfile(filepath):
        error = _FILTER_DOES_NOT_EXIST_ERROR.format(rule.description)
        raise ExpectedError(error, rule.line_number, context.current_filepath)

    import_ = _Import(filepath, blockname, templates)
    if any(import_ == previous for previous in context.imports):
        error = _create_circular_reference_error(rule.description, context.imports, import_)
        raise ExpectedError(error, rule.line_number, context.current_filepath)

    return import_

def _get_segment_text(segment: _ImportSegment, match: re.Match[str], rule: Rule, context: ImportContext):
    text = match.group(segment.name)
    if text is None:
        return text

    if not segment.allows_empty and text == "":
        error = _EMPTY_SEGMENT_ERROR.format(rule.description, segment.name)
        raise ExpectedError(error, rule.line_number, context.current_filepath)

    for splitter in _Splitter:
        if splitter in text:
            error = _SEGMENT_FORMAT_ERROR.format(
                rule.description,
                segment.name,
                text,
                splitter.name.lower(),
                splitter)
            raise ExpectedError(error, rule.line_number, context.current_filepath)

    return text

def _get_filter(filepath: str, context: ImportContext):
    absolute_filepath = os.path.abspath(filepath)

    if absolute_filepath not in context.cache:
        context.cache[absolute_filepath] = Filter.load(filepath)

    return context.cache[absolute_filepath]

def _get_block(filter: Filter, blockname: str):
    for block in filter.blocks:
        if blockname == _get_blockname(block):
            return block
    error = _BLOCK_NOT_FOUND_ERROR.format(blockname)
    raise ExpectedError(error, filepath=filter.filepath)

def _get_blockname(block: Block):
    name_rules = block.get_rules(_NAME_RULE)
    return name_rules[-1].description if len(name_rules) > 0 else None

def _parse_rule_filepath(root: str, navigation: str, rule: Rule, context: ImportContext):
    if navigation == "":
        return context.current_filepath
    
    root_dir = _transform_root_to_dir(root, rule, context)
    filepath = _transform_navigation_to_real_path(navigation)
    return _get_full_filepath(root_dir, filepath)

def _transform_root_to_dir(root: str | None, rule: Rule, context: ImportContext):
    match root:
        case None:
            root_dir = os.path.dirname(context.current_filepath)
        case "":
            root_dir = os.path.dirname(context.original_filepath)
        case _ if root not in context.roots:
            error = _ROOT_NOT_FOUND_ERROR.format(root, rule.description)
            raise ExpectedError(error, rule.line_number, context.current_filepath)
        case _:
            path_prefix = os.path.dirname(context.original_filepath)
            path_suffix = _transform_navigation_to_real_path(context.roots[root])
            root_dir = os.path.join(path_prefix, path_suffix)

    return re.sub("([\\w\\.])$", "\\1/", root_dir)

def _transform_navigation_to_real_path(navigation: str):
    real_path = re.sub(f"\\s*{_Navigation.IN}\\s*", "/", navigation)
    real_path = re.sub(f"\\s*{_Navigation.OUT}\\s*", "../", real_path)
    return re.sub("([^\\.^/])\\.", "\\1/.", real_path)

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