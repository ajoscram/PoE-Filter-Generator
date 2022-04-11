import os.path

import classes.section
from common import util
from classes.filter import Filter
from classes.generator_error import GeneratorError
from classes.rule import Rule
from classes.section import Section

_NAME = "append"
_SPLITTER = "->"
_SECTION_NAME = "name"

_INCORRECT_RULE_FORMAT_ERROR = "The {0} '{1}' is formatted incorrectly. Make sure your append rules look like this:\n\n\tfile > path > to > filter -> section_name"
_EMPTY_SECTION_NAME_ERROR = "The {0} '{1}' has no section name. Make sure to provide one after the arrow."
_SECTION_NOT_FOUND_ERROR = "The section with name '{0}' was not found."

_filter_cache: dict[str, Filter] = {}

def handle(filter: Filter, section: Section, _):
    """Handles appends of lines to sections. Options are ignored."""
    new_section = Section(section.line_number)
    params = _get_initial_params(filter.filepath, section)
    for line in _get_lines(section, filter.filepath, params):
        new_section.append(line)
    return [ new_section ]

def _get_initial_params(filepath: str, section: Section):
    name_rules = section.get_rules(_SECTION_NAME)
    if len(name_rules) > 0:
        return [ { "filepath": filepath, "section_name": name_rules[-1].description } ]
    else:
        return []

def _get_lines(section: Section, filepath: str, previous_params: list[dict[str, str]]):
    lines = []
    line_index = 0
    for rule in section.get_rules(_NAME):
        lines_to_append = _get_lines_to_append(rule, filepath, previous_params)
        lines += section.lines[line_index : rule.line_number - section.line_number + 1]
        lines += [ line for line in lines_to_append if _line_is_valid(line) ]
        line_index = rule.line_number - section.line_number + 1
    return lines + section.lines[line_index :]

def _get_lines_to_append(rule: Rule, filepath: str, previous_params: list[dict[str, str]]):
    params = _parse_rule_params(rule, filepath, previous_params)
    append_filter = _get_filter(params["filepath"])
    append_section = _get_section(append_filter, params["section_name"])
    return _get_lines(append_section, append_filter.filepath, previous_params + [ params ])

def _parse_rule_params(rule: Rule, current_filepath: str, previous_params: list[dict[str, str]]):
    parts = rule.description.split(_SPLITTER)
    if len(parts) != 2:
        util.raise_rule_error(_INCORRECT_RULE_FORMAT_ERROR, current_filepath, rule)
    
    filepath = util.parse_rule_filepath(current_filepath, parts[0].strip())
    if not os.path.exists(filepath):
        util.raise_rule_error(util.DOES_NOT_EXIST_ERROR, current_filepath, rule)

    section_name = parts[1].strip()
    if section_name == "":
        util.raise_rule_error(_EMPTY_SECTION_NAME_ERROR, current_filepath, rule)
    
    params = { "filepath": filepath, "section_name": section_name }
    if any(_are_params_equal(params, previous) for previous in previous_params):
        util.raise_rule_error(util.CIRCULAR_REFERENCE_ERROR, current_filepath, rule)

    return params

def _get_filter(filepath: str):
    absolute_filepath = os.path.abspath(filepath)

    if absolute_filepath not in _filter_cache:
        _filter_cache[absolute_filepath] = Filter(filepath)

    return _filter_cache[absolute_filepath]

def _get_section(filter: Filter, section_name: str):
    for section in filter.sections:
        for rule in section.get_rules(_SECTION_NAME):
            if rule.description == section_name:
                return section
    raise GeneratorError(_SECTION_NOT_FOUND_ERROR.format(section_name), filepath=filter.filepath)

def _line_is_valid(line: str):
    show_start = line.lstrip().startswith(classes.section._SHOW)
    hide_start = line.lstrip().startswith(classes.section._HIDE)
    return not show_start and not hide_start

def _are_params_equal(first: dict[str, str], second: dict[str, str]):
    same_filter = os.path.samefile(first["filepath"], second["filepath"])
    same_section = first["section_name"] == second["section_name"]
    return same_filter and same_section