"""Module that exports the Rule class only."""

from classes.generator_error import GeneratorError

class Rule:
    """A rule is a bit of data that can be parsed by generators.
    
    Rules have these fields:
        line_number: the file line number where the rule is found.
        name: the name which identifies the rule.
        description: any extra data needed for the rule. Can be omitted.
    Rules are included in comments inside lines and start with #. (hashtag and a dot).
    Multiple rules can be declared in the same line, separated by . (dot).
    Names and descriptions in a rule are separated by : (colon), like name:description.
    """

    RULE_SEPARATOR = '.'
    RULE_START = '#' + RULE_SEPARATOR
    RULE_FIELD_SEPARATOR = ':'

    EMPTY_NAME_ERROR = "Empty name (probably an extra '.')"
    EMPTY_DESCRIPTION_ERROR = "Empty description (probably an extra ':' or forgot a description to a rule)"
    TOO_MANY_FIELDS_ERROR = "Too many fields (probably an extra ':')"

    def __init__(self, line_number: int, name: str, description: str):
        """Rule constructor which receives the line_number where the rule is found, the name which identifies the rule and its description optionally for any additional data."""
        self.line_number: int = line_number
        self.name: str = name
        self.description: str = description
    
    def __str__(self):
        return '[' + str(self.line_number) + '] "' + self.name + '" : "' + self.description + '"'

    @classmethod
    def extract(cls, line_number: int, line: str):
        """Returns all rules in a line as a list of rules."""
        rules = []
        try:
            line = line[line.index(Rule.RULE_START) + len(Rule.RULE_START):]
            rule_strings = line.split(Rule.RULE_SEPARATOR)
            for rule_string in rule_strings:
                
                fields = rule_string.split(Rule.RULE_FIELD_SEPARATOR)
                if len(fields) > 2:
                    raise GeneratorError(Rule.TOO_MANY_FIELDS_ERROR, line_number)

                name = fields[0].strip()
                if name == '':
                    raise GeneratorError(Rule.EMPTY_NAME_ERROR, line_number)
                
                description = fields[1].strip() if len(fields) == 2 else ""
                if description == '' and len(fields) == 2:
                    raise GeneratorError(Rule.EMPTY_DESCRIPTION_ERROR, line_number)
                
                rules.append(Rule(line_number, name, description))
        except ValueError:
            pass
        return rules