import web
from typing import Callable
from core import ExpectedError, Sieve, Operand
from web import Expiration
from . import base_validation, class_, gem
from .constants import Field

_URL = "https://repoe-fork.github.io/base_items.min.json"

_BASE_NAME_NOT_FOUND_ERROR = """The base item name '{0}' could not be identified when attempting to get its class name.

\tThis problem is likely solved by deleting PFG's cache with the command [cyan]pfg :clean[/cyan]."""

def get_bases(sieve: Sieve) -> set[str]:
    """Returns the set of base type names that match the `sieve` received."""
    bases = _get_sieved_bases(sieve, _get_pattern_for_bases)
    return { base_info[Field.NAME] for base_info in bases.values() }

def get_class_for_base(base_name: str) -> str:
    """Returns the item class name associated to the `base_name` received."""

    # hardcoded results as they cannot currently be obtained from RePoE
    # left untested because this should be removed eventually
    if "Piece" in base_name or base_name in [ "Vaal Aspect", "Primordial Fragment" ]:
        return "Pieces"
    if "Allflame Ember" in base_name:
        return "Embers of the Allflame"

    bases = _get_bases()
    base_name = _get_searchable_base_name(base_name, bases)                                                        
    return bases[base_name][Field.FILTER_ITEM_CLASS]

def get_domains_and_tags(sieve: Sieve) -> tuple[set[str], set[str]]:
    """Returns a tuple that contains a set of domain and tag names for base items
    that match the `sieve` received."""
    tags = set()
    domains = set()
    bases = _get_sieved_bases(sieve, _get_pattern_for_tags)
    for base_info in bases.values():
        domains.add(base_info[Field.DOMAIN])
        tags.update(base_info[Field.TAGS])
    return (domains, tags)

def _get_bases() -> dict[str]:
    return web.get(_URL, Expiration.MONTHLY, formatter=_format_bases_info)

def _format_bases_info(bases_json: dict[str, dict]):
    return {
        base_info[Field.NAME]: _get_formatted_base_info(base_info)
        for base_id, base_info in bases_json.items()
        if base_validation.validate(base_id, base_info) }

def _get_formatted_base_info(base_info: dict[str]):
    filter_item_class = class_.get_filter_item_class(base_info[Field.CLASS])
    base_info[Field.FILTER_ITEM_CLASS] = filter_item_class
    return base_info

def _get_sieved_bases(sieve: Sieve, pattern_generator: Callable[[dict[str]], dict[str]]):
    bases = _get_bases()
    return { base_name: base_info
        for base_name, base_info in bases.items()
        if pattern_generator(base_info) in sieve }

def _get_pattern_for_tags(base_info: dict[str]):
    return {
        Operand.CLASS: base_info[Field.FILTER_ITEM_CLASS],
        Operand.DROP_LEVEL: base_info[Field.DROP_LEVEL],
        Operand.BASE_TYPE: base_info[Field.NAME] }

def _get_pattern_for_bases(base_info: dict[str]):
    return {
        Operand.CLASS: base_info[Field.FILTER_ITEM_CLASS],
        Operand.DROP_LEVEL: base_info[Field.DROP_LEVEL] }

def _get_searchable_base_name(name: str, bases: dict[str]):
    if name in bases:
        return name

    if base_gem_name := gem.try_get_gem_base(name):
        return base_gem_name
    
    raise ExpectedError(_BASE_NAME_NOT_FOUND_ERROR.format(name))