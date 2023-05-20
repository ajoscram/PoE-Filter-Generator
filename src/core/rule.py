from .generator_error import GeneratorError

RULE_SEPARATOR = '.'
COMMENT_START = '#'
RULE_START = COMMENT_START + RULE_SEPARATOR

_EMPTY_NAME_ERROR = "Empty name (probably an extra '.')"
_EMPTY_DESCRIPTION_ERROR = "Empty description (probably an extra ':' or forgot a description to a rule)"
_TOO_MANY_FIELDS_ERROR = "Too many fields (probably an extra ':')"

class Rule:
    """A rule is a bit of data that can be parsed by generators.
    They are included in comments inside lines and start with #. (hashtag and a dot).
    Multiple rules can be declared in the same line, separated by . (dot).
    Names and descriptions in a rule are separated by : (colon), like name:description.
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
        rules = []
        if cls._should_extract(text):
            text = text[text.index(RULE_START) + len(RULE_START):]
            rule_strings = text.split(RULE_SEPARATOR)
            for rule_string in rule_strings:
                
                fields = rule_string.split(maxsplit=1)
                if len(fields) > 2:
                    raise GeneratorError(_TOO_MANY_FIELDS_ERROR, line_number)

                name = fields[0].strip()
                if name == '':
                    raise GeneratorError(_EMPTY_NAME_ERROR, line_number)
                
                description = fields[1].strip() if len(fields) == 2 else ""
                if description == '' and len(fields) == 2:
                    raise GeneratorError(_EMPTY_DESCRIPTION_ERROR, line_number)
                
                rules.append(Rule(line_number, name, description))
        return rules

    @classmethod
    def _should_extract(cls, text: str):
        split_text = text.split(RULE_START)
        return len(split_text) >= 2 and not COMMENT_START in split_text[0]

    def __str__(self):
        return f'[{self.line_number}] "{self.name}": "{self.description}"'
