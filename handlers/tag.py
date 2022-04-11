from classes.generator_error import GeneratorError
from classes.section import Section

_NAME = "tag"
_EMPTY_TAG_ERROR = "You must provide at least a tag for the 'tag' {0}."

def handle(_, section: Section, options:list[str]):
    """Hides or shows sections based on their tags.
    Every option with the exception of the last is treated as a tag category.
    The last option is the tag inside that category."""
    if options == []:
        raise GeneratorError(_EMPTY_TAG_ERROR.format("handler"))

    command_category = options[:-1]
    command_tag = options[-1]

    for rule in section.get_rules(_NAME):
        split_description = rule.description.split()
        if split_description == []:
            raise GeneratorError(_EMPTY_TAG_ERROR.format("rule"), rule.line_number)

        rule_category = split_description[:-1]
        rule_tag = split_description[-1]

        if command_category == rule_category:
            if command_tag == rule_tag:
                section.show()
            else:
                section.hide()

    return [ section ]