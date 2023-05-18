import re

from .generator_error import GeneratorError
from .rule import Rule, COMMENT_START

_MULTILINE_STRING_ERROR = "Multiline string"
_BOOL_VALUE_ERROR = "Could not translate the value(s) in the line to either 'True' or 'False'. Make sure to provide exactly one of either those values."
_INT_VALUE_ERROR = "Could not translate the value(s) in the line to a digit. Make sure to provide exactly one numeric value."

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
    
    def get_value_as_boolean(self):
        """Returns the line's value as a boolean.
        An error is returned if the line contains more than one value or the value cannot be parsed to a boolean."""
        if len(self.values) == 1:
            value = self.values[0].lower()
            if value == "true":
                return True
            if value == "false":
                return False
        raise GeneratorError(_BOOL_VALUE_ERROR, self.number)
    
    def get_value_as_int(self):
        """Returns the line's value as an integer.
        An error is returned if the line contains more than one value or the value cannot be parsed to a integer."""
        if len(self.values) == 1 and self.values[0].isdigit():
            return int(self.values[0])
        raise GeneratorError(_INT_VALUE_ERROR, self.number)
    
    def contains(self, pattern: str, exclude_comments: bool = False):
        """Returns whether or not this line contains the pattern.
        Comments are optionally excluded form this check with `exclude_comments`."""
        text = str(self).split(COMMENT_START, 1)[0] if exclude_comments else str(self)
        return pattern in text
    
    def get_rules(self, name_or_names: str | list[str]):
        """Gets every rule within the line with a name equal to or included in `name_or_names`."""
        if type(name_or_names) == str:
            name_or_names = [ name_or_names ]
        return [ rule for rule in self.rules if rule.name in name_or_names ]
    
    def comment_out(self):
        """Comments the line out by prepending a # to the line's text."""
        self._set_parts(COMMENT_START + str(self))

    def __str__(self):
        values = " ".join(self.values)
        parts = [ self.operand, self.operator, values, self.comment ]
        parts = [ part for part in parts if part != "" ]
        return self.indentation + " ".join(parts)
    
    def _set_parts(self, text: str):
        parts = re.search(_LINE_REGEX, text.rstrip()).groups()
        self.indentation:str = parts[0] or ""
        self.operand: str = parts[1] or ""
        self.operator: str = parts[2] or ""
        self.values: list[str] = re.findall(_SINGLE_VALUE_REGEX, parts[3] or "")
        self.comment: str = parts[4] or ""
        self.rules: list[Rule] = Rule.extract(self.number, self.comment)
