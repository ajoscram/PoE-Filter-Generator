import re

from classes.block import Block
from classes.filter import Filter
from classes.line import Line
from classes.rule import Rule, COMMENT_START, RULE_START

_NAME = "format"

_INDEX_TAG = "index"
_SECTION_TAG = "sec"
_SUBSECTION_TAG = "subsec"

_NEWLINE = "\n"
_LINE_PADDING = "-"
_MAX_LINE_LENGTH = 80 - len(COMMENT_START)
_SECTION_SEPARATOR = COMMENT_START + _LINE_PADDING * _MAX_LINE_LENGTH

class _Section:
    def __init__(self, rule: Rule, section_id: int, subsection_id: int):
        self.rule = rule
        self.name = rule.description.split()[1]
        self.id = f"[{section_id}_{subsection_id}]"
        self.is_subsection = subsection_id != 0

_index: list[_Section] = None

def handle(filter: Filter, block: Block, _):
    """Formats the contents of the filter and adds indices and sections for order."""
    global _index
    _index = _create_index(filter) if _index == None else _index
    
    raw_lines = [ raw_line for line in block.lines for raw_line in _get_raw_lines(line) ]

    if block == filter.blocks[0] and raw_lines[0] == _NEWLINE:
        raw_lines = raw_lines[1:]
    
    if block != filter.blocks[-1] and raw_lines[-1] != _NEWLINE:
        raw_lines += [ _NEWLINE ]

    return Block.extract(raw_lines, block.line_number)

def _create_index(filter: Filter):
    sections: list[_Section] = []
    section_id = 0
    subsection_id = 0
    for rule in [ rule for block in filter.blocks for rule in block.get_rules(_NAME) ]:
        _validate_format_rule(rule)
        if not rule.description.startswith(_INDEX_TAG):
            section_id += 1 if rule.description.startswith(_SECTION_TAG) else 0
            subsection_id = subsection_id + 1 if rule.description.startswith(_SUBSECTION_TAG) else 0
            sections += [ _Section(rule, section_id, subsection_id) ]
    return sections

def _validate_format_rule(rule: Rule):
    parts = rule.description.split()
    pass

def _get_raw_lines(line: Line):
    raw_line = _format(line.text)
    raw_lines = [ raw_line ] if raw_line.strip() != "" else []
    for rule in line.get_rules(_NAME):
        raw_lines += [ _NEWLINE ]
        if rule.description.startswith(_INDEX_TAG):
            raw_lines += _get_index_lines()
        elif rule.description.startswith(_SECTION_TAG):
            section = _find_section_in_index(rule)
            raw_lines += _get_section_lines(section)
        elif rule.description.startswith(_SUBSECTION_TAG):
            section = _find_section_in_index(rule)
            raw_lines += [ _get_subsection_line(section) ]
    return raw_lines

def _format(raw_line: str):
    if not COMMENT_START in raw_line.split(RULE_START)[0]:
        raw_line = re.sub("#\..+", "", raw_line)
    return raw_line.rstrip()

def _find_section_in_index(rule: Rule):
    global _index
    return next(section for section in _index if section.rule == rule)

def _get_index_lines():
    global _index
    lines = _get_index_header_lines()
    for section in _index:
        if not section.is_subsection:
            lines += [ COMMENT_START ]
        indent = ' ' * (8 if section.is_subsection else 4)
        lines += [ _render_line(f"{indent}{section.name} ", "", f" {section.id}", ".") ]
    return lines

def _get_section_lines(section: _Section):
    return [
        _SECTION_SEPARATOR,
        _render_line("", section.name, section.id),
        _SECTION_SEPARATOR
    ]

def _get_subsection_line(section: _Section):
    return _render_line(f" {section.name} ", "", f" {section.id}", _LINE_PADDING)

def _render_line(left_text: str, center_text: str, right_text: str, padding_token: str = " "):
    padding = padding_token * (_MAX_LINE_LENGTH  - len(left_text) - len(center_text) - len(right_text))
    padding_split_index = (len(padding) - len(right_text) - len(left_text)) // 2
    return COMMENT_START + left_text + padding[padding_split_index:] + center_text + padding[:padding_split_index] + right_text

def _get_index_header_lines():
    return [
        _SECTION_SEPARATOR,
        _render_line("", "INDEX", ""),
        _SECTION_SEPARATOR,
        COMMENT_START,
        _render_line("", "CTRL+F the IDs to jump to any section in the document.", ""),
    ]