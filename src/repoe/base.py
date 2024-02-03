import web, re
from typing import Callable
from core import ExpectedError, Sieve, CLASS, BASE_TYPE, DROP_LEVEL
from web import Expiration
from . import class_
from .constants import NAME_FIELD, DOMAIN_FIELD

_URL = "https://lvlvllvlvllvlvl.github.io/RePoE/base_items.min.json"

_TAGS_FIELD = "tags"
_CLASS_FIELD = "item_class"
_DROP_LEVEL_FIELD = "drop_level"
_RELEASE_STATE_FIELD = "release_state"
_FILTER_ITEM_CLASS_FIELD = "filter_item_class"

_RELEASED_RELEASE_STATE = "released"
_UNIQUE_ONLY_RELEASE_STATE = "unique_only"

_UNDEFINED_DOMAIN = "undefined"
_INVALID_DOMAINS = [ _UNDEFINED_DOMAIN, "map_device", "watchstone" ]
_VALID_UNDEFINED_DOMAIN_CLASSES = [
    "StackableCurrency",
    "DivinationCard",
    "IncubatorStackable",
    "MapFragment",
    "DelveStackableSocketableCurrency",
    "QuestItem" ]

_INVALID_ID_PATTERNS = [
    # Deprecated or duplicate base types
    "Royale", "Quiver\\d+", "Talisman\\d*_\\d*_[^1]",
    # Previous map series identifiers
    "Shaped", "MapTier", "Map2Tier", "MapTier", "MapAtlas", "MapWorldsHarbingerMid", "MapWorldsHarbingerHigh" ]

_BASE_NAME_NOT_FOUND_ERROR = """The base item name '{0}' could not be identified when attempting to get its class name.

\tThis problem is likely solved by deleting PFG's cache with the command [cyan]pfg :clean[/cyan]."""

def get_bases(sieve: Sieve) -> set[str]:
    """Returns the set of base type names that match the `sieve` received."""
    bases = _get_sieved_bases(sieve, _get_pattern_for_bases)
    return { base_info[NAME_FIELD] for base_info in bases.values() }

def get_class_for_base(base_name: str) -> str:
    """Returns the item class name associated to the `base_name` received."""

    # hardcoded results as they cannot currently be obtained from RePoE
    # left untested because this should be removed eventually
    if "Piece" in base_name:
        return "Pieces"
    if "Maven's Invitation" in base_name:
        return "Misc Map Items"

    bases = _get_bases()
    if base_name not in bases:
        raise ExpectedError(_BASE_NAME_NOT_FOUND_ERROR.format(base_name))
                                                            
    return bases[base_name][_FILTER_ITEM_CLASS_FIELD]

def get_domains_and_tags(sieve: Sieve) -> tuple[set[str], set[str]]:
    """Returns a tuple that contains a set of domain and tag names for base items
    that match the `sieve` received."""
    tags = set()
    domains = set()
    bases = _get_sieved_bases(sieve, _get_pattern_for_tags)
    for base_info in bases.values():
        domains.add(base_info[DOMAIN_FIELD])
        tags.update(base_info[_TAGS_FIELD])
    return (domains, tags)

def _get_bases():
    return web.get(_URL, expiration=Expiration.MONTHLY, formatter=_format_bases_info)

def _format_bases_info(bases_json: dict[str, dict]):
    item_classes = class_.get_classes()
    return {
        base_info[NAME_FIELD]: _get_formatted_base_info(base_info, item_classes)
        for base_id, base_info in bases_json.items()
        if _is_base_valid(base_id, base_info) }

def _get_formatted_base_info(base_info: dict[str], item_classes: dict[str]):
    item_class_name = base_info[_CLASS_FIELD]
    filter_item_class_name = item_classes[item_class_name][NAME_FIELD]
    base_info[_FILTER_ITEM_CLASS_FIELD] = filter_item_class_name
    return base_info

def _is_base_valid(base_id: str, base_info: dict[str]):
    return base_info[_RELEASE_STATE_FIELD] == _UNIQUE_ONLY_RELEASE_STATE \
        or _is_base_id_valid(base_id) and _is_base_info_valid(base_info)

def _is_base_info_valid(base_info: dict[str]):
    released = base_info[_RELEASE_STATE_FIELD] == _RELEASED_RELEASE_STATE
    valid_domain = _is_domain_valid(base_info[DOMAIN_FIELD], base_info[_CLASS_FIELD])
    return released and valid_domain

def _is_domain_valid(domain: str, class_: str):
    if domain not in _INVALID_DOMAINS: 
        return True

    domain_is_undefined = domain == _UNDEFINED_DOMAIN
    has_valid_undefined_tag = class_ in _VALID_UNDEFINED_DOMAIN_CLASSES
    return domain_is_undefined and has_valid_undefined_tag

def _is_base_id_valid(base_id: str):
    base_name = base_id.split("/")[-1]
    return all(re.search(pattern, base_name) == None for pattern in _INVALID_ID_PATTERNS)

def _get_sieved_bases(sieve: Sieve, pattern_generator: Callable[[dict[str]], dict[str]]):
    bases: dict[str] = _get_bases()
    return { base_name: base_info
        for base_name, base_info in bases.items()
        if pattern_generator(base_info) in sieve }

def _get_pattern_for_tags(base_info: dict[str]):
    return {
        CLASS: base_info[_FILTER_ITEM_CLASS_FIELD],
        DROP_LEVEL: base_info[_DROP_LEVEL_FIELD],
        BASE_TYPE: base_info[NAME_FIELD]
    }

def _get_pattern_for_bases(base_info: dict[str]):
    return {
        CLASS: base_info[_FILTER_ITEM_CLASS_FIELD],
        DROP_LEVEL: base_info[_DROP_LEVEL_FIELD],
    }