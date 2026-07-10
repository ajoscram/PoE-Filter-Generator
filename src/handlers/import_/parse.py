import os, re, utils
from core import Rule, ExpectedError
from .import_ import Import
from .import_context import ImportContext
from .import_segment import ImportSegment, NamedImportSegment, SplitterImportSegment
from .constants import Navigation, Splitter

_ROOT_SEGMENT = SplitterImportSegment(Splitter.ROOT, r"(?:(?P<{name}>.*?)\s*\{splitter})", allows_empty=True)
_NAVIGATION_SEGMENT = NamedImportSegment("navigation", r"(?P<{name}>.*?)")
_BLOCKNAME_SEGMENT = SplitterImportSegment(Splitter.BLOCKNAME, r"(?:{splitter}\s*(?P<{name}>.*?))")
_TEMPLATE_SEGMENT = SplitterImportSegment(Splitter.TEMPLATE, r"(?:{splitter}\s*(?P<{name}>.*?))")

_FILTER_EXTENSION = ".filter"
_IMPORT_REGEX = fr"^\s*{_ROOT_SEGMENT.regex}?\s*{_NAVIGATION_SEGMENT.regex}\s*{_BLOCKNAME_SEGMENT.regex}?\s*{_TEMPLATE_SEGMENT.regex}?\s*$"

_FILTER_DOES_NOT_EXIST_ERROR = "Could not resolve the import '{0}' to a filter file on your disk."
_ROOT_NOT_FOUND_ERROR = "The root '{0}' in import '{1}' was not received via the handler's options."

_SEGMENT_ERROR_PRELUDE = "The import '{0}' is formatted incorrectly. "
_SEGMENT_FORMAT_ERROR = _SEGMENT_ERROR_PRELUDE + "It's {1} '{2}' contains a {3} separator (`{4}`)."
_EMPTY_SEGMENT_ERROR = _SEGMENT_ERROR_PRELUDE + "It's {1} is empty."

_CIRCULAR_REFERENCE_ERROR = "The import '{0}' creates a circular reference loop:\n{1}"
_LOOP_STARTS_HERE_ERROR_TEXT = " (LOOP STARTS HERE)"
_LOOP_REPEATS_HERE_ERROR_TEXT = " (LOOP REPEATS HERE)"

def extract(rule: Rule, context: ImportContext):
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

    import_ = Import(filepath, blockname, templates)
    if any(import_ == previous for previous in context.imports):
        error = _create_circular_reference_error(rule.description, context.imports, import_)
        raise ExpectedError(error, rule.line_number, context.current_filepath)

    return import_

def _get_segment_text(segment: ImportSegment, match: re.Match[str], rule: Rule, context: ImportContext):
    text = match.group(segment.name)
    if text is None:
        return text

    if not segment.allows_empty and text == "":
        error = _EMPTY_SEGMENT_ERROR.format(rule.description, segment.name)
        raise ExpectedError(error, rule.line_number, context.current_filepath)

    for splitter in Splitter:
        if splitter in text:
            error = _SEGMENT_FORMAT_ERROR.format(
                rule.description,
                segment.name,
                text,
                splitter.name.lower(),
                splitter)
            raise ExpectedError(error, rule.line_number, context.current_filepath)

    return text

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
    real_path = re.sub(f"\\s*{Navigation.IN}\\s*", "/", navigation)
    real_path = re.sub(f"\\s*{Navigation.OUT}\\s*", "../", real_path)
    return re.sub("([^\\.^/])\\.", "\\1/.", real_path)

def _get_full_filepath(root_dir: str, filepath_suffix: str):
    filepath = root_dir + filepath_suffix + _FILTER_EXTENSION
    filepath = os.path.normpath(filepath)
    return re.sub("\\\\", "/", filepath)

def _create_circular_reference_error(rule_description: str, previous_imports: list[Import], looped_import: Import):
    import_trace = ""
    for import_ in previous_imports:
        import_trace += f"\n\t{import_}"
        if looped_import == import_:
            import_trace += _LOOP_STARTS_HERE_ERROR_TEXT
    import_trace += f"\n\t{looped_import}{_LOOP_REPEATS_HERE_ERROR_TEXT}"
    return _CIRCULAR_REFERENCE_ERROR.format(rule_description, import_trace)