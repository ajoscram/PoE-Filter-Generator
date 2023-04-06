import re

from .generator_error import GeneratorError
from .rule import Rule, COMMENT_START

_MULTILINE_STRING_ERROR = "Multiline string"

_BLOCK_STARTERS = [ "Show", "Hide", "Minimal" ]
_INDENTATION_REGEX = "\s*"
_OPERAND_REGEX = "[A-Za-z]*"
_VALUES_REGEX = f"[^{COMMENT_START}]+"
_COMMENT_REGEX = f"{COMMENT_START}.*"
_OPERATOR_REGEX = "[<|>|=|!|<|>]=?\d*"
_LINE_REGEX = f"^({_INDENTATION_REGEX})({_OPERAND_REGEX})\s*({_OPERATOR_REGEX})?\s*({_VALUES_REGEX})?({_COMMENT_REGEX})?$"
_SINGLE_VALUE_REGEX = '"[^"]+"|\w+'

class Line:
    """
    A line represents a line of text inside a Block, which may include rules in it.
    Rules are extracted upon creation.
    Multiline strings are not allowed as text.
    """
    
    def __init__(self, text: str, number: int):
        text = text.rstrip()
        if '\n' in text:
            raise GeneratorError(_MULTILINE_STRING_ERROR, number)
        self.number: int = number
        self._set_parts(text)

    def is_block_starter(self):
        """Returns whether or not this line should start a new Block."""
        return self.operand in _BLOCK_STARTERS
    
    def contains(self, pattern: str):
        """Returns whether or not this line contains the pattern.
        Comments are excluded from this check."""
        return pattern in str(self).split(COMMENT_START, 1)[0]

    def contains_in_comment(self, pattern: str):
        """Returns whether or not this line contains the pattern within comments."""
        return pattern in self.comment

    def is_empty(self):
        """Returns whtether or not this line is comprised entirely of whitespace."""
        return str(self).strip() == ""
    
    def comment_out(self):
        """Comments the line out by prepending a # to the line's text."""
        self._set_parts(COMMENT_START + str(self))
    
    def uncomment(self):
        """Removes the left-most # (hashtag) of a line.
        If the line has no comments then this does nothing."""
        split_text = str(self).split(COMMENT_START, 1)
        if len(split_text) == 2:
            self._set_parts(split_text[0] + split_text[1])
    
    def get_rules(self, name_or_names: str | list[str]):
        """Gets every rule within the line with a name equal to rule_name."""
        if type(name_or_names) == str:
            name_or_names = [ name_or_names ]
        return [ rule for rule in self.rules if rule.name in name_or_names ]

    def __str__(self):
        values = " ".join(self.values)
        parts = [ self.indentation + self.operand, self.operator, values, self.comment ]
        parts = [ part for part in parts if part != "" ]
        return " ".join(parts)
    
    def _set_parts(self, text: str):
        parts = re.search(_LINE_REGEX, text.rstrip()).groups()
        self.indentation:str = parts[0] or ""
        self.operand: str = parts[1] or ""
        self.operator: str = parts[2] or ""
        self.values: list[str] = re.findall(_SINGLE_VALUE_REGEX, parts[3] or "")
        self.comment: str = parts[4] or ""
        self.rules: list[Rule] = Rule.extract(self.number, self.comment)
