from core import Block, ExpectedError
from .context import Context

NAME = "tag"
_WILDCARD = "_"
_HANDLER = "handler"
_RULE = "rule"

_EMPTY_TAG_ERROR = "You must provide at least a tag for the 'tag' {0}."

def handle(block: Block, context: Context):
    """Hides or shows blocks based on their tags.
    Every option with the exception of the last is treated as a tag category.
    The last option is the tag inside that category."""
    handler_category, handler_tag = _get_category_and_tag(context.options, _HANDLER)

    for rule in block.get_rules(NAME):

        split_description = rule.description.split()
        rule_category, rule_tag = _get_category_and_tag(split_description, _RULE, rule.line_number)

        if not _are_categories_equivalent(rule_category, handler_category):
            continue

        if _is_text_equivalent(rule_tag, handler_tag):
            block.show()
        else:
            block.hide()
    
    return block.get_raw_lines()

def _is_text_equivalent(first: str, second: str):
    return first == second or _WILDCARD in [ first, second ]

def _are_categories_equivalent(rule_category: list[str], handler_category: list[str]):
    return len(rule_category) == len(handler_category) and \
        all(_is_text_equivalent(x, y) for x, y in zip(rule_category, handler_category))

def _get_category_and_tag(tag_path: list[str], error_descriptor: str, line_number: int = None):
    if len(tag_path) == 0:
        raise ExpectedError(_EMPTY_TAG_ERROR.format(error_descriptor), line_number)
    category = tag_path[:-1]
    tag = tag_path[-1]
    return (category, tag)