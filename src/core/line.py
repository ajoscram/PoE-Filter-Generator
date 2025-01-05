import re
from .rule import Rule
from .expected_error import ExpectedError
from .constants import Delimiter, BLOCK_STARTERS

_MULTILINE_STRING_ERROR = "Multiline string"

_INDENTATION_REGEX = "\\s*"
_OPERAND_REGEX = f"[^\\s{Delimiter.COMMENT_START}]*"
_VALUES_REGEX = f"[^{Delimiter.COMMENT_START}]+"
_COMMENT_REGEX = f"{Delimiter.COMMENT_START}.*"
_OPERATOR_REGEX = "[<|>|=|!]=?\\d*"
_LINE_REGEX = f"^({_INDENTATION_REGEX})({_OPERAND_REGEX})\\s*({_OPERATOR_REGEX})?\\s*({_VALUES_REGEX})?({_COMMENT_REGEX})?$"
_SINGLE_VALUE_REGEX = '"[^"]*"|-?\\w+'

class Line:
    """
    A Line represents a line of text inside a Block, which may include rules in it.
    Rules are extracted upon creation.
    Multiline strings are not allowed as text.
    """
    def __init__(self, text: str, number: int):
        """
        * `text`: the text in the line. Passing in a string with a new-line character raisesan error.
        * `number`: The line's number in a filter file.
        """
        text = text.rstrip()
        if '\n' in text:
            raise ExpectedError(_MULTILINE_STRING_ERROR, number)
        self.number: int = number
        self._set_parts(text)

    def is_block_starter(self):
        """Returns whether or not this line should start a new Block."""
        return self.operand in BLOCK_STARTERS
    
    def has_filter_info(self):
        """Returns `True` if the line contains any item filter information."""
        return self.operand != "" or self.operator != "" or len(self.values) > 0

    def has_rules(self):
        """Returns `True` if the line contains any `Rule`s."""
        return len(self.rules) > 0
    
    def has_comment(self):
        """Returns `True` if the line has a non-rule comment."""
        return self.comment != "" and not self.has_rules()
    
    def is_empty(self):
        """Returns `True` if the line contains no text other than whitespace."""
        return not (self.has_filter_info() or self.has_rules() or self.has_comment())
    
    def get_rules(self, name_or_names: str | list[str]):
        """Gets every rule within the line with a name equal to or included in `name_or_names`."""
        if isinstance(name_or_names, str):
            name_or_names = [ name_or_names ]
        return [ rule for rule in self.rules if rule.name in name_or_names ]
    
    def comment_out(self):
        """Comments the line out by prepending a `#.#` to the line's text."""
        self._set_parts(Delimiter.COMMENT_RULE_START + str(self))

    def __contains__(self, string: str):
        """Returns whether or not this line contains the string."""
        return string in str(self)

    def __str__(self):
        values = " ".join(self.values)
        parts = [ self.operand, self.operator, values, self.comment ]
        parts = [ part for part in parts if part != "" ]
        return self.indentation + " ".join(parts)
    
    def _set_parts(self, text: str):
        parts = re.search(_LINE_REGEX, text).groups()
        self.indentation: str = parts[0] or ""
        self.operand: str = parts[1] or ""
        self.operator: str = parts[2] or ""
        self.values: list[str] = re.findall(_SINGLE_VALUE_REGEX, parts[3] or "")
        self.comment: str = parts[4] or ""
        self.rules: list[Rule] = Rule.extract(self.number, self.comment)
