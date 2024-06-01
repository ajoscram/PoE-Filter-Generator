import re, utils
from core import Delimiter, Block, Filter, Rule, ExpectedError

NAME = "alias"
_ALIAS_SEPARATOR = "="
_ALIAS_RULE_PATTERN = f"\\{Delimiter.RULE_SEPARATOR}{NAME}[^\\{Delimiter.RULE_SEPARATOR}]*"

_INCORRECT_RULE_FORMAT_ERROR = "The alias '{0}' is formatted incorrectly. Make sure it looks like this:\n\n\talias_name = replacement text"

_EMPTY_PARAMETER_ERROR = "Empty alias {0} on '{1}'."
_REPLACEMENT_ERROR_DESCRIPTOR = "replacement"
_ALIAS_NAME_ERROR_DESCRIPTOR = "name"

_DUPLICATE_ALIAS_NAME_ERROR = "The alias name '{0}' was already declared on line {1}."
_CONTAINED_ALIAS_NAME_ERROR = "The alias name '{0}' {1} the alias name '{2}' which is declared on line {3}."
_IS_CONTAINED_BY_ERROR_DESCRIPTOR = "is contained by"
_CONTAINS_ERROR_DESCRIPTOR = "contains"

class _Alias:
    def __init__(self, name: str, replacement: str, source_rule: Rule):
        self.name = name
        self.replacement = replacement
        self.source_rule = source_rule

_aliases: list[_Alias] = None

def handle(filter: Filter, block: Block, _):
    """Finds and replaces aliased text for a replacement.
    Text within `.alias` rules is excempt from replacement."""
    global _aliases
    _aliases = _aliases or _get_aliases_from_filter(filter)
    return [ _get_aliased_line(raw_line, _aliases)
        for raw_line in block.get_raw_lines() ]

def _get_aliases_from_filter(filter: Filter):
    rules = [ rule 
        for block in filter.blocks
        for rule in block.get_rules(NAME) ]
    
    aliases: list[_Alias] = []
    for rule in rules:
        alias = _get_alias_from_rule(rule, aliases)
        aliases += [ alias ]

    return aliases

def _get_alias_from_rule(rule: Rule, aliases: list[_Alias]):
    parts = rule.description.split(_ALIAS_SEPARATOR)
    if len(parts) != 2:
        error = _INCORRECT_RULE_FORMAT_ERROR.format(rule.description)
        raise ExpectedError(error, rule.line_number)
    
    name = parts[0].rstrip()
    if name == "":
        error = _EMPTY_PARAMETER_ERROR.format(_ALIAS_NAME_ERROR_DESCRIPTOR, rule.description)
        raise ExpectedError(error, rule.line_number)

    replacement = parts[1].lstrip()
    if replacement == "":
        error = _EMPTY_PARAMETER_ERROR.format(_REPLACEMENT_ERROR_DESCRIPTOR, rule.description)
        raise ExpectedError(error, rule.line_number)

    for alias in aliases:
        if name == alias.name:
            error = _DUPLICATE_ALIAS_NAME_ERROR.format(name, alias.source_rule.line_number)
            raise ExpectedError(error, rule.line_number)
        if name in alias.name:
            error = _CONTAINED_ALIAS_NAME_ERROR.format(
                name, _IS_CONTAINED_BY_ERROR_DESCRIPTOR, alias.name, alias.source_rule.line_number)
            raise ExpectedError(error, rule.line_number)
        if alias.name in name:
            error = _CONTAINED_ALIAS_NAME_ERROR.format(
                name, _CONTAINS_ERROR_DESCRIPTOR, alias.name, alias.source_rule.line_number)
            raise ExpectedError(error, rule.line_number)

    return _Alias(name, replacement, rule)

def _get_aliased_line(raw_line: str, aliases: list[_Alias]):
    temp_aliases = _get_temp_aliases(raw_line)

    for temp_alias, raw_rule in temp_aliases.items():
        raw_line = raw_line.replace(raw_rule, temp_alias)

    for alias in aliases:
        raw_line = raw_line.replace(alias.name, alias.replacement)

    for temp_alias, raw_rule in temp_aliases.items():
        raw_line = raw_line.replace(temp_alias, raw_rule)

    return raw_line

def _get_temp_aliases(raw_line: str):
    raw_rules = re.findall(_ALIAS_RULE_PATTERN, raw_line)
    temp_aliases: dict[str, str] = {}
    
    for raw_rule in raw_rules:
        temp_alias = utils.get_random_str()
        temp_aliases[temp_alias] = raw_rule
    
    return temp_aliases