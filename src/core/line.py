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
    A line represents a line of text inside a Block, which may include rules in it.
    Rules are extracted upon creation.
    Multiline strings are not allowed as text.
    """
    def __init__(self, text: str, number: int):
        """
        * `text`: the text in the line. Passing in a string with a new-line character raisesan error.
        * `number`: The line's number in the file.
        """
        text = text.rstrip()
        if '\n' in text:
            raise ExpectedError(_MULTILINE_STRING_ERROR, number)
        self.number: int = number
        self._set_parts(text)

    def is_block_starter(self):
        """Returns whether or not this line should start a new Block."""
        return self.operand in BLOCK_STARTERS
    
    def is_empty(self, exclude_comments: bool = False):
        """Returns `True` if the line contains no text other than whitespace.
        Comments are optionally excluded with `exclude_comments`."""
        text = self._get_text(exclude_comments)
        return len(text.strip()) == 0

    def contains(self, string: str, exclude_comments: bool = False):
        """Returns whether or not this line contains the string.
        Comments are optionally excluded with `exclude_comments`."""
        return string in self._get_text(exclude_comments)
    
    def get_rules(self, name_or_names: str | list[str]):
        """Gets every rule within the line with a name equal to or included in `name_or_names`."""
        if isinstance(name_or_names, str):
            name_or_names = [ name_or_names ]
        return [ rule for rule in self.rules if rule.name in name_or_names ]
    
    def comment_out(self):
        """Comments the line out by prepending a `#` to the line's text."""
        self._set_parts(Delimiter.COMMENT_START + str(self))

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
    
    def _get_text(self, exclude_comments: bool):
        return str(self).split(Delimiter.COMMENT_START, 1)[0] if exclude_comments else str(self)
