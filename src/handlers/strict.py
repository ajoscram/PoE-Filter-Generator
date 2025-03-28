from core import Block, ExpectedError
from .context import Context

NAME = "strict"
_HANDLER = "handler"
_RULE = "rule"
_STRICTNESS_ERROR_PREFIX = "You must provide only 1 integer value for the strictness {0}."
_STRICTNESS_ARG_COUNT_ERROR = _STRICTNESS_ERROR_PREFIX + " You've provided {1} arguments."
_STRICTNESS_ARG_TYPE_ERROR =  _STRICTNESS_ERROR_PREFIX + " You've provided '{1}'."

def handle(block: Block, context: Context):
    """Handles creation of strictness subfilters.
    Only one option is accepted and it should include the strictness value to use."""
    handler_strictness = _get_handler_strictness(context.options)

    for rule in block.get_rules(NAME):
        if not rule.description.isdigit():
            raise ExpectedError(_STRICTNESS_ARG_TYPE_ERROR.format(_RULE, rule.description), rule.line_number)
        
        rule_strictness = int(rule.description)
        
        if rule_strictness >= handler_strictness:
            block.show()
        else:
            block.hide()

    return block.get_raw_lines()

def _get_handler_strictness(options: list[str]):
    if len(options) != 1:
        raise ExpectedError(_STRICTNESS_ARG_COUNT_ERROR.format(_HANDLER, len(options)))

    if not options[0].strip().isdigit():
        raise ExpectedError(_STRICTNESS_ARG_TYPE_ERROR.format(_HANDLER, options[0]))

    return int(options[0])