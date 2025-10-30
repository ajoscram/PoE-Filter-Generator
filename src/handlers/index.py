from core import Delimiter, Rule, Line, Block, Filter, ExpectedError
from .context import Context

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

_SUBSECTION_MISSING_PARENT_SECTION_ERROR = "The subsection '{0}' was declared before any section that could parent it."

class IndexContext(Context):
    def __init__(self, filter, options):
        super().__init__(filter, options)
        self.index = _Index(filter)

class _Id:
    def __init__(self, major: int = 0, minor: int = 0):
        self.major = major
        self.minor = minor        
        self.length = 0

    def update(self, rule: Rule):
        if rule.name == _SECTION_RULE_NAME:
            self.major += 1
            self.minor = 0
        elif rule.name == _SUBSECTION_RULE_NAME:
            self.minor += 1
        
        major_length = len(str(self.major))
        minor_length = len(str(self.minor))
        self.length = max(major_length, minor_length, self.length)

    def _pad(self, sub_id: int):
        return _ID_PADDING * (self.length - len(str(sub_id))) + str(sub_id)

    def __str__(self):
        padded_major = self._pad(self.major)
        padded_minor = self._pad(self.minor)
        return f"[{padded_major}_{padded_minor}]"

class _Index:
    def __init__(self, filter: Filter):
        id = _Id()
        self._sections: list[_Section] = [ self._get_section(rule, id)
            for block in filter.blocks
            for rule in block.get_rules(_SECTION_RULE_NAMES) ]
        for section in self._sections:
            section.id.length = id.length
    
    def get_lines(self, rule: Rule):
        if rule.name == _INDEX_RULE_NAME:
            return self._get_index_lines(rule.description)
        return self._get_section_lines(rule)

    def _get_section(self, rule: Rule, id: _Id):

        if id.major == 0 and rule.name == _SUBSECTION_RULE_NAME:
            raise ExpectedError(_SUBSECTION_MISSING_PARENT_SECTION_ERROR.format(rule.description), rule.line_number)

        id.update(rule)
        return _Section(rule, _Id(id.major, id.minor))

    def _get_index_lines(self, description: str):
        return self._get_header_lines(description) + [ line
            for section in self._sections
            for line in section.get_index_lines() ]

    def _get_header_lines(self, description: str):
        title_lines = [ _render_line("", "", description) ] if description != "" else []
        return title_lines + [
            _SECTION_SEPARATOR,
            _render_line("", _INDEX_HEADER, ""),
            _SECTION_SEPARATOR,
            Delimiter.COMMENT_START,
            _render_line("", _INDEX_HINT, "") ]

    def _get_section_lines(self, rule: Rule):
        section = next(section for section in self._sections if section.rule == rule)
        return section.get_rule_lines()

class _Section:
    def __init__(self, rule: Rule, id: _Id):
        self.rule = rule
        self.id = id

    def get_rule_lines(self):
        is_subsection = self._is_subsection()
        line = _render_line(
            f" {self.rule.description} " if is_subsection else "",
            "" if is_subsection else self.rule.description,
            f" {self.id}",
            _LINE_PADDING if is_subsection else " ")
        return [ line ] if is_subsection else [ _SECTION_SEPARATOR, line, _SECTION_SEPARATOR ]

    def get_index_lines(self):
        is_subsection = self._is_subsection()
        line = _render_line(
            f"{' ' * (8 if is_subsection else 4)}{self.rule.description} ",
            "",
            f" {self.id}",
            ".")
        return [ line ] if is_subsection else [ Delimiter.COMMENT_START, line ]
    
    def _is_subsection(self):
        return self.rule.name == _SUBSECTION_RULE_NAME

def handle(block: Block, context: IndexContext):
    """Adds indices and addressable sections."""
    return [ raw_line
        for line in block.lines
        for raw_line in _get_raw_lines_from_line(line, context.index) ]

def _get_raw_lines_from_line(line: Line, index: _Index):
    raw_lines = [ rule_line
        for rule in line.get_rules(_RULE_NAMES)
        for rule_line in index.get_lines(rule) ]
    
    if len(raw_lines) > 0:
        raw_lines = [ "\n" ] + raw_lines + [ "\n" ]

    return [ str(line) ] + raw_lines

def _render_line(left_text: str, center_text: str, right_text: str, padding_token: str = " "):
    padding = padding_token * (_MAX_LINE_LENGTH  - len(left_text) - len(center_text) - len(right_text))
    padding_split_index = (len(padding) - len(right_text) - len(left_text)) // 2
    return Delimiter.COMMENT_START + left_text + padding[padding_split_index:] + center_text + padding[:padding_split_index] + right_text