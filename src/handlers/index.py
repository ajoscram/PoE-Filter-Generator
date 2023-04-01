from src.core.block import Block
from src.core.filter import Filter
from src.core.line import Line
from src.core.rule import Rule, COMMENT_START

_INDEX_RULE_NAME = "index"
_SECTION_RULE_NAME = "section"
_SUBSECTION_RULE_NAME = "subsection"
_SECTION_RULE_NAMES = [ _SECTION_RULE_NAME, _SUBSECTION_RULE_NAME ]
_RULE_NAMES = [ _INDEX_RULE_NAME ] + _SECTION_RULE_NAMES

_LINE_PADDING = "-"
_MAX_LINE_LENGTH = 80 - len(COMMENT_START)
_SECTION_SEPARATOR = COMMENT_START + _LINE_PADDING * _MAX_LINE_LENGTH

class _Section:
    def __init__(self, rule: Rule, section_id: int, subsection_id: int):        
        self.rule = rule
        self.name = rule.description
        
        self.id = f"[{section_id}_{subsection_id}]"
        self.is_subsection = subsection_id != 0

_index: list[_Section] = None

def handle(filter: Filter, block: Block, _):
    """Adds indices and addressable sections. Options are ignored."""
    global _index
    _index = _create_index(filter) if _index == None else _index
    return [ raw_line for line in block.lines for raw_line in _get_raw_lines_from_line(line) ]

def _create_index(filter: Filter):
    sections: list[_Section] = []
    section_id = 0
    subsection_id = 0
    for rule in [ rule for block in filter.blocks for rule in block.get_rules(_SECTION_RULE_NAMES) ]:
        section_id += 1 if rule.name  == _SECTION_RULE_NAME else 0
        subsection_id = subsection_id + 1 if rule.name == _SUBSECTION_RULE_NAME else 0
        sections += [ _Section(rule, section_id, subsection_id) ]
    return sections

def _get_raw_lines_from_line(line: Line):
    raw_lines = [ line.text ]
    for rule in line.get_rules(_RULE_NAMES):
        raw_lines += [ "\n" ] +  _get_raw_lines_from_rule(rule) + [ "\n" ]
    return raw_lines

def _get_raw_lines_from_rule(rule: Rule):
    if rule.name  == _INDEX_RULE_NAME:
        return _get_index_lines()
    
    section = _find_section_in_index(rule)
    if rule.name == _SECTION_RULE_NAME:
        return _get_section_lines(section)
    else:
        return [ _get_subsection_line(section) ]

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

def _get_index_header_lines():
    return [
        _SECTION_SEPARATOR,
        _render_line("", "INDEX", ""),
        _SECTION_SEPARATOR,
        COMMENT_START,
        _render_line("", "CTRL+F the IDs to jump to any section in the document.", ""),
    ]

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