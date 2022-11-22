from classes.generator_error import GeneratorError
from classes.block import Block

_NAME = "strict"
_STRICTNESS_ERROR_PREFIX = "You must provide only 1 integer value for the strictness {0}."
_STRICTNESS_ARG_COUNT_ERROR = _STRICTNESS_ERROR_PREFIX + " You've provided {1} arguments."
_STRICTNESS_ARG_TYPE_ERROR =  _STRICTNESS_ERROR_PREFIX + " You've provided '{1}'."

def handle(_, block: Block, options:list[str]):
    """Handles creation of strictness subfilters.
    Only one option is accepted and it should include the strictness value to use."""
    if len(options) != 1:
        raise GeneratorError(_STRICTNESS_ARG_COUNT_ERROR.format("handler", len(options)))

    if not options[0].strip().isdigit():
        raise GeneratorError(_STRICTNESS_ARG_TYPE_ERROR.format("handler", options[0]))

    command_strictness = int(options[0])

    for rule in block.get_rules(_NAME):
        if not rule.description.isdigit():
            raise GeneratorError(_STRICTNESS_ARG_TYPE_ERROR.format("rule", rule.description), rule.line_number)
        
        rule_strictness = int(rule.description)
        
        if rule_strictness >= command_strictness:
            block.show()
        else:
            block.hide()

    return [ block ]