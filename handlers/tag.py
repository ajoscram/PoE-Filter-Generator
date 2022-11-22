from pickle import FALSE
from classes.generator_error import GeneratorError
from classes.block import Block

_NAME = "tag"
_WILDCARD = "_"
_EMPTY_TAG_ERROR = "You must provide at least a tag for the 'tag' {0}."

def handle(_, block: Block, options: list[str]):
    """Hides or shows blocks based on their tags.
    Every option with the exception of the last is treated as a tag category.
    The last option is the tag inside that category."""
    if options == []:
        raise GeneratorError(_EMPTY_TAG_ERROR.format("handler"))

    command_category = options[:-1]
    command_tag = options[-1]
    tag_index = len(options) - 1

    for rule in block.get_rules(_NAME):
        split_description = rule.description.split()
        
        if split_description == []:
            raise GeneratorError(_EMPTY_TAG_ERROR.format("rule"), rule.line_number)

        if len(split_description) < len(options):
            continue

        rule_category = split_description[:tag_index]
        rule_tag = split_description[tag_index]

        if _are_categories_equivalent(command_category, rule_category):
            if _is_text_equivalent(rule_tag, command_tag):
                block.show()
            else:
                block.hide()
    return [ block ]

def _is_text_equivalent(first: str, second: str):
    return first == second or first == _WILDCARD or second == _WILDCARD

def _are_categories_equivalent(first: list[str], second: list[str]):
    if len(first) != len(second):
        return False

    for i in range(len(first)):
        if not _is_text_equivalent(first[i], second[i]):
            return False
    
    return True