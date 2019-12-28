class Rule:
    """A rule is a bit of data that can be parsed by generators.
    
    Rules have these fields:
        line_number: the file line number where the rule is found.
        tag: the tag which identifies the rule.
        description: any extra data needed for the rule. Can be omitted.
    Rules are included in comments inside lines and start with #. (hashtag and a dot).
    Multiple rules can be declared in the same line, separated by . (dot).
    Tags and descriptions in a rule are separated by : (colon), like tag:description.
    """

    RULE_START = '#.'
    RULE_SEPARATOR = '.'
    RULE_FIELD_SEPARATOR = ':'

    def __init__(self, line_number: int, tag: str, description: str = ""):
        """Rule constructor which receives the line_number where the rule is found, the tag which identifies the rule and its description optionally for any additional data."""
        self.line_number = line_number
        self.tag = tag
        self.description = description
    
    def __str__(self):
        return '[' + str(self.line_number) + '] "' + self.tag + '" : "' + self.description + '"'

    @classmethod
    def extract(cls, line_number: int, line: str):
        """Returns all rules in a line as a list of rules."""
        rules = []
        try:
            line = line[line.index(cls.RULE_START) + len(cls.RULE_START):]
            rule_strings = line.split(cls.RULE_SEPARATOR)
            for rule_string in rule_strings:
                fields = rule_string.split(cls.RULE_FIELD_SEPARATOR)
                if(len(fields) == 1):
                    fields[0] = fields[0].strip()
                    if(fields[0] == ''):
                        raise RuleError(line_number, RuleError.EMPTY_TAG)
                    rules.append(Rule(line_number, fields[0]))
                elif(len(fields) == 2):
                    fields[0] = fields[0].strip()
                    fields[1] = fields[1].strip()
                    if(fields[0] == ''):
                        raise RuleError(line_number, RuleError.EMPTY_TAG)
                    if(fields[1] == ''):
                        raise RuleError(line_number, RuleError.EMPTY_DESCRIPTION)
                    rules.append(Rule(line_number, fields[0], fields[1]))
                else:
                    raise RuleError(line_number, RuleError.TOO_MANY_FIELDS)
        except ValueError:
            pass
        return rules

class RuleError(Exception):
    """Class for rule exception handling."""

    #Error message constants
    EMPTY_TAG = "Empty tag (probably an extra '.')"
    EMPTY_DESCRIPTION = "Empty description (probably an extra ':' or forgot a description to a rule)"
    TOO_MANY_FIELDS = "Too many fields (probably an extra ':')"

    def __init__(self, line_number: int, message: str):
        """Takes a message from the caller and a line number where the error occurred."""
        self.message = message
        self.line_number = line_number