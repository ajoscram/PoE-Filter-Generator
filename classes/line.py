from classes.generator_error import GeneratorError
from classes.rule import Rule

_SHOW = "Show"
_HIDE = "Hide"
_COMMENT_START = '#'

_MULTILINE_STRING_ERROR = "Multiline string"

class Line:
    """
    A line represents a line of text inside a Block, which may include rules in it.
    Rules are extracted upon creation.
    Multiline strings are not allowed as text.
    """
    
    def __init__(self, text: str, number: int):
        self.text: str = text.rstrip()
        if '\n' in self.text:
            raise GeneratorError(_MULTILINE_STRING_ERROR, number)
        
        self.number: int = number
        self.rules: list[Rule] = Rule.extract(number, text)
    
    def is_block_starter(self):
        """Returns whether or not this line should start a new Block."""
        stripped_text = self.text.lstrip()
        return stripped_text.startswith(_SHOW) or stripped_text.startswith(_HIDE)
    
    def contains(self, pattern: str):
        """Returns whether or not this line contains the pattern.
        Comments are excluded from this check."""
        return pattern in self.text.split(_COMMENT_START, 1)[0]

    def contains_in_comment(self, pattern: str):
        """Returns whether or not this line contains the pattern within comments."""
        split_text = self.text.split(_COMMENT_START, 1)
        if len(split_text) == 1:
            return False
        return pattern in split_text[1]

    def comment(self):
        "Comments the line out by prepending a # to the line's text."
        self.text += _COMMENT_START
    
    def uncomment(self):
        """Removes the left-most # (hashtag) of a line.
        If the line has no comments then this does nothing."""
        split_text = self.text.split(_COMMENT_START, 1)
        if len(split_text) == 2:
            self.text = split_text[0] + split_text[1]
    
    def get_rules(self, rule_name: str):
        """Gets every rule within the line with a name equal to rule_name."""
        return [ rule for rule in self.rules if rule.name == rule_name ]
    
    def __str__(self):
        string = f'[{self.number}] "{self.text}"'
        for rule in self.rules:
            string += f"\n\t{rule}"
        return string