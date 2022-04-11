from classes.generator_error import GeneratorError
from classes.section import Section

NAME = "strict"
STRICTNESS_ERROR_PREFIX = "You must provide only 1 integer value for the strictness {0}."
STRICTNESS_ARG_COUNT_ERROR = STRICTNESS_ERROR_PREFIX + " You've provided {1} arguments."
STRICTNESS_ARG_TYPE_ERROR =  STRICTNESS_ERROR_PREFIX + " You've provided '{1}'."

def handle(_, section: Section, options:list[str]):
    """Handles creation of strictness subfilters.
    Only one option is accepted and it should include the strictness value to use."""
    if len(options) != 1:
        raise GeneratorError(STRICTNESS_ARG_COUNT_ERROR.format("handler", len(options)))

    if not options[0].strip().isdigit():
        raise GeneratorError(STRICTNESS_ARG_TYPE_ERROR.format("handler", options[0]))

    command_strictness = int(options[0])

    for rule in section.get_rules(NAME):
        if not rule.description.strip().isdigit():
            raise GeneratorError(STRICTNESS_ARG_TYPE_ERROR.format("rule", rule.description), rule.line_number)
        
        rule_strictness = int(rule.description)
        
        if rule_strictness >= command_strictness:
            section.show()
        else:
            section.hide()

    return [ section ]