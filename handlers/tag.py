"""Handles creation of subfilters based on tags.
Tags can be categorized by adding their categories to them prior to them.
Categories nest and are used to group tags.

When invoked, the last option passed in is used as the tag.
Every preceding category must match, otherwise it is ignored.
Every differing tag in the same category will be hidden.

Usage:
    python generate.py input.filter [output.filter] .tag [ancestor_catgory ... child_category] tag
Output:
    - output.filter
"""
from classes.generator_error import GeneratorError
from classes.section import Section

NAME = "tag"
EMPTY_TAG_ERROR_MESSAGE = "You must provide at least a tag for the 'tag' {0}."

def handle(_, section: Section, options:list):
    """Hides or shows sections based on their tags.
    Every option with the exception of the last is treated as a tag category.
    The last option is the tag inside that category."""

    if options == []:
        raise GeneratorError(EMPTY_TAG_ERROR_MESSAGE.format("handler"))

    command_category = options[:-1]
    command_tag = options[-1]

    for rule in section.get_rules(NAME):
        split_description = rule.description.split()
        if split_description == []:
            raise GeneratorError(EMPTY_TAG_ERROR_MESSAGE.format("rule"), rule.line_number)

        rule_category = split_description[:-1]
        rule_tag = split_description[-1]

        if command_category == rule_category:
            if command_tag == rule_tag:
                section.show()
            else:
                section.hide()

    return [ section ]