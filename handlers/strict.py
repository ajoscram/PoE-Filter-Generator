"""Handles creation of strictness subfilters.
If a single option is passed then a file is created.
If multiple options are passed then a folder is created instead, with one filter for each option.
The higher the tier the better.

Usage:
    python generate.py input.filter [output.filter] .strict tier
Output:
    - output.filter
"""
from classes.generator_error import GeneratorError
from classes.section import Section

NAME = "strict"
INCORRECT_STRICTNESS_PREFIX = "You must provide only 1 integer value for the strictness {0}."
INCORRECT_STRICTNESS_ARG_COUNT = INCORRECT_STRICTNESS_PREFIX + " You've provided {1} arguments."
INCORRECT_STRICTNESS_ARG_TYPE =  INCORRECT_STRICTNESS_PREFIX + " You've provided '{1}'."

def handle(_, section: Section, options:list):
    """Handles creation of strictness subfilters.
    Only one option is accepted and it should include the strictness value to use.
    """

    if len(options) != 1:
        raise GeneratorError(INCORRECT_STRICTNESS_ARG_COUNT.format("handler", len(options)))

    if not options[0].strip().isdigit():
        raise GeneratorError(INCORRECT_STRICTNESS_ARG_TYPE.format("handler", options[0]))

    command_strictness = int(options[0])

    for rule in section.get_rules(NAME):
        if not rule.description.strip().isdigit():
            raise GeneratorError(INCORRECT_STRICTNESS_ARG_TYPE.format("rule", rule.description), rule.line_number)
        
        rule_strictness = int(rule.description)
        
        if rule_strictness >= command_strictness:
            section.show()
        else:
            section.hide()

    return [ section ]