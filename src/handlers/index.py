from core import Delimiter, Rule, Line, Block, Filter

_INDEX_RULE_NAME = "index"
_SECTION_RULE_NAME = "section"
_SUBSECTION_RULE_NAME = "subsection"
_SECTION_RULE_NAMES = [ _SECTION_RULE_NAME, _SUBSECTION_RULE_NAME ]
_RULE_NAMES = [ _INDEX_RULE_NAME ] + _SECTION_RULE_NAMES
NAME = _INDEX_RULE_NAME

_ID_PADDING = "0"
_LINE_PADDING = "-"
_MAX_LINE_LENGTH = 80 - len(Delimiter.COMMENT_START)
_SECTION_SEPARATOR = Delimiter.COMMENT_START + _LINE_PADDING * _MAX_LINE_LENGTH

_INDEX_HEADER = "INDEX"
_INDEX_HINT = "CTRL+F the IDs to jump to any section in the document."

def handle(filter: Filter, block: Block, _):
    """Adds indices and addressable sections. Options are ignored."""
    global _index
    _index = _index or _Index(filter)
    
    lines = [ raw_line
        for line in block.lines
        for raw_line in _get_raw_lines_from_line(line, _index) ]
    
    if block == filter.blocks[-1]:
        _index = None
    
    return lines

class _Index:
    def __init__(self, filter: Filter):
        self.subid_length = 0
        self._sections: list[_Section] = []

        rules = (rule
            for block in filter.blocks
            for rule in block.get_rules(_SECTION_RULE_NAMES))
    
        for rule in rules:
            self.append(rule)
    
    def append(self, rule: Rule):
        section_list = self._sections[-1].subsections \
            if rule.name == _SUBSECTION_RULE_NAME else self._sections
        
        section = _Section(rule, len(section_list) + 1)
        section_list.append(section)

        new_id_length = len(str(len(section_list)))
        if new_id_length > self.subid_length:
            self.subid_length = new_id_length
    
    def get_lines(self, rule: Rule):
        if rule.name == _INDEX_RULE_NAME:
            return self._get_index_lines()
        return self._get_section_lines(rule)

    def _get_index_lines(self):
        lines = self._get_header_lines()
        for section in self._sections:
            lines += section.get_lines_for_index(self.subid_length)
            section_id = section.get_padded_subid(self.subid_length)
            for subsection in section.subsections:
                lines += subsection.get_lines_for_index(
                    self.subid_length, section_id)
        return lines

    def _get_section_lines(self, rule: Rule):
        for section in self._sections:
            if section.rule == rule:
                return section.get_lines_for_rule(self.subid_length)
            if subsection := next((sub for sub in section.subsections if sub.rule == rule), None):
                section_id = section.get_padded_subid(self.subid_length)
                return subsection.get_lines_for_rule(self.subid_length, section_id)
        raise RuntimeError(f"'{rule}' was not registered in .index's index. This should never happen.")
    
    def _get_header_lines(self):
        return [
            _SECTION_SEPARATOR,
            _render_line("", _INDEX_HEADER, ""),
            _SECTION_SEPARATOR,
            Delimiter.COMMENT_START,
            _render_line("", _INDEX_HINT, "") ]

class _Section:
    def __init__(self, rule: Rule, subid: int):
        self._subid = str(subid)
        self.rule = rule
        self.subsections: list[_Section] = []

    def get_lines_for_rule(self, id_length: int, parent_id: str | None = None):
        id = self.get_id(id_length, parent_id)
        if self._is_subsection():
            return [ _render_line(
                f" {self.rule.description} ", "", f" {id}", _LINE_PADDING) ]

        return [
            _SECTION_SEPARATOR,
            _render_line("", self.rule.description, id),
            _SECTION_SEPARATOR ]

    def get_lines_for_index(self, id_length: int, parent_id: str | None = None):
        id = self.get_id(id_length, parent_id)
        indent = ' ' * (8 if self._is_subsection() else 4)
        lines = [ Delimiter.COMMENT_START ] if not self._is_subsection() else []
        lines += [ _render_line(f"{indent}{self.rule.description} ", "", f" {id}", ".") ]
        return lines

    def get_id(self, id_length: int, parent_padded_id: str | None = None):
        padded_subid = self.get_padded_subid(id_length)
        if parent_padded_id != None:
            return f"[{parent_padded_id}_{padded_subid}]"
        return f"[{padded_subid}_{_ID_PADDING * id_length}]"

    def get_padded_subid(self, id_length: int):
        return _ID_PADDING * (id_length - len(self._subid)) + self._subid

    def _is_subsection(self):
        return self.rule.name == _SUBSECTION_RULE_NAME

def _get_raw_lines_from_line(line: Line, index: _Index):
    raw_lines = [ rule_line
        for rule in line.get_rules(_RULE_NAMES)
        for rule_line in index.get_lines(rule) ]
    return [ str(line), "\n" ] + raw_lines + [ "\n" ]

def _render_line(left_text: str, center_text: str, right_text: str, padding_token: str = " "):
    padding = padding_token * (_MAX_LINE_LENGTH  - len(left_text) - len(center_text) - len(right_text))
    padding_split_index = (len(padding) - len(right_text) - len(left_text)) // 2
    return Delimiter.COMMENT_START + left_text + padding[padding_split_index:] + center_text + padding[:padding_split_index] + right_text

_index: _Index = None