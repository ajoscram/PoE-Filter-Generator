from .generator_error import GeneratorError
from .constants import COMMENT_START, RULE_SEPARATOR, RULE_START

_EMPTY_RULE_ERROR = "Empty rule (probably an extra '.')"

class Rule:
    """A rule is a bit of data that can be parsed by generators.
    They are included in comments inside lines and start with #. (hashtag and a dot).
    Multiple rules can be declared in the same line, separated by . (dot).
    Names and descriptions in a rule are separated by whitespace.
    Rules have these fields:
        * line_number: the file line number where the rule is found.
        * name: the name which identifies the rule.
        * description: any extra data needed for the rule. Can be omitted.
    """
    def __init__(self, line_number: int, name: str, description: str):
        """Rule constructor which receives the line_number where the rule is found, the name which identifies the rule and its description optionally for any additional data."""
        self.line_number: int = line_number
        self.name: str = name
        self.description: str = description
    
    @classmethod
    def extract(cls, line_number: int, text: str):
        """Returns all rules in a text as a list of rules."""
        if not _should_extract(text):
            return []
        text = text[text.index(RULE_START) + len(RULE_START):]
        rule_strings = text.split(RULE_SEPARATOR)
        return [ _get_rule(rule_string, line_number) for rule_string in rule_strings ]

def _should_extract(text: str):
    split_text = text.split(RULE_START)
    return len(split_text) >= 2 and not COMMENT_START in split_text[0]

def _get_rule(text: str, line_number: int):
    if text.strip() == "":
        raise GeneratorError(_EMPTY_RULE_ERROR, line_number)
    fields = text.split(maxsplit=1)
    name = fields[0].strip()
    description = fields[1].strip() if len(fields) == 2 else ""
    return Rule(line_number, name, description)
