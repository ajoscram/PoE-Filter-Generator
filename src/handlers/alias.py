import re, utils
from core import Delimiter, Block, Filter, Rule, ExpectedError
from .context import Context

NAME = "alias"

_OPTIONS_SOURCE_NAME = "the handler's options"
_RULE_SOURCE_NAME = "line {0}"

_ALIAS_PARTS_PATTERN = f"([^{Delimiter.PAIR_SEPARATOR}]*){Delimiter.PAIR_SEPARATOR}(.*)"
_ALIAS_ENTRIES_PATTERN = f"([^{Delimiter.LIST_ENTRY_SEPARATOR}]+){Delimiter.LIST_ENTRY_SEPARATOR}?"
_ALIAS_RULE_PATTERN = f"\\{Delimiter.RULE_SEPARATOR}{NAME}[^\\{Delimiter.RULE_SEPARATOR}]*"

_ALIAS_FORMAT_ERROR = "The alias '{0}' is formatted incorrectly. Make sure it looks like this:\n\n\talias_name = replacement text"
_EMPTY_PARAMETER_ERROR = "Empty alias {0} on '{1}'."
_REPLACEMENT_ERROR_DESCRIPTOR = "replacement"
_ALIAS_NAME_ERROR_DESCRIPTOR = "name"

_DUPLICATE_ALIAS_NAME_ERROR = "The alias name '{0}' was already declared on {1}."
_CONTAINED_ALIAS_NAME_ERROR = "The alias name '{0}' {1} the alias name '{2}' which is declared on {3}."
_IS_CONTAINED_BY_ERROR_DESCRIPTOR = "is contained by"
_CONTAINS_ERROR_DESCRIPTOR = "contains"

class _Source:
    def __init__(self, name: str, raw_text: str, line_number: int | None = None):
        self.name = name
        self.raw_text = raw_text
        self.line_number = line_number
    
    @classmethod
    def from_options(cls, raw_text: str):
        return _Source(_OPTIONS_SOURCE_NAME, raw_text)

    @classmethod
    def from_rule(cls, raw_text: str, rule: Rule):
        name = _RULE_SOURCE_NAME.format(rule.line_number)
        return _Source(name, raw_text, rule.line_number)

class _Alias:
    def __init__(self, name: str, replacement: str, source: _Source):
        self.name = name
        self.replacement = replacement
        self.source = source

class AliasContext(Context):
    def __init__(self, filter: Filter, options: list[str]):
        super().__init__(filter, options)
        self.aliases: list[_Alias] = _get_aliases(filter, options)

def handle(block: Block, context: AliasContext):
    """Finds and replaces aliased text for a replacement.
    Text within `.alias` rules is excempt from replacement.
    Additional aliases can be passed in via the options and are interpreted as any other alias rule."""
    return [ _get_aliased_line(raw_line, context.aliases)
        for raw_line in block.get_raw_lines() ]

def _get_aliases(filter: Filter, options: list[str]):
    aliases = [ _get_alias(_Source.from_options(entry))
        for entry in re.findall(_ALIAS_ENTRIES_PATTERN, " ".join(options)) ]
    
    aliases += [ _get_alias(_Source.from_rule(entry, rule))
        for block in filter.blocks
        for rule in block.get_rules(NAME)
        for entry in re.findall(_ALIAS_ENTRIES_PATTERN, rule.description) ]
    
    _validate_aliases(aliases)
    return aliases

def _get_alias(source: _Source):
    parts = re.match(_ALIAS_PARTS_PATTERN, source.raw_text)
    if parts == None or len(parts.groups()) != 2:
        error = _ALIAS_FORMAT_ERROR.format(source.raw_text)
        raise ExpectedError(error, source.line_number)
    
    name = parts[1].strip()
    if name == "":
        error = _EMPTY_PARAMETER_ERROR.format(_ALIAS_NAME_ERROR_DESCRIPTOR, source.raw_text)
        raise ExpectedError(error, source.line_number)

    replacement = parts[2].strip()
    if replacement == "":
        error = _EMPTY_PARAMETER_ERROR.format(_REPLACEMENT_ERROR_DESCRIPTOR, source.raw_text)
        raise ExpectedError(error, source.line_number)
    
    return _Alias(name, replacement, source)

def _validate_aliases(aliases: list[_Alias]) -> None:
    match aliases:
        case [ head, *tail ]:
            for alias in tail:
                _validate_duplicate_aliases(head, alias)
            return _validate_aliases(tail)
        case _:
            return

def _validate_duplicate_aliases(first: _Alias, second: _Alias):
    if second.name == first.name:
        error = _DUPLICATE_ALIAS_NAME_ERROR.format(second.name, first.source.name)
        raise ExpectedError(error, second.source.line_number)
    
    if second.name in first.name:
        error = _CONTAINED_ALIAS_NAME_ERROR.format(
            second.name, _IS_CONTAINED_BY_ERROR_DESCRIPTOR, first.name, first.source.name)
        raise ExpectedError(error, second.source.line_number)
    
    if first.name in second.name:
        error = _CONTAINED_ALIAS_NAME_ERROR.format(
            second.name, _CONTAINS_ERROR_DESCRIPTOR, first.name, first.source.name)
        raise ExpectedError(error, second.source.line_number)

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