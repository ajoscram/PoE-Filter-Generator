from classes.generator_error import GeneratorError
from classes.block import Block

_NAME = "tag"
_EMPTY_TAG_ERROR = "You must provide at least a tag for the 'tag' {0}."

def handle(_, block: Block, options:list[str]):
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

        if len(split_description) <= tag_index:
            continue

        rule_category = split_description[:tag_index]
        rule_tag = split_description[tag_index]

        if command_category == rule_category:
            if command_tag == rule_tag:
                block.show()
            else:
                block.hide()
    return [ block ]