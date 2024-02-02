import web
from . import base
from web import Expiration
from core import Sieve, ITEM_LEVEL
from .constants import NAME_FIELD, DOMAIN_FIELD

_URL = "https://lvlvllvlvllvlvl.github.io/RePoE/mods.min.json"

_TAG_FIELD = "tag"
_WEIGHT_FIELD = "weight"
_SPAWN_WEIGHTS_FIELD = "spawn_weights"
_REQUIRED_LEVEL_FIELD = "required_level"
_GENERATION_TYPE_FIELD = "generation_type"

_VALID_GENERATION_TYPES = [ "prefix", "suffix" ]

def get_mods(sieve: Sieve) -> set[str]:
    """Returns the names of mods that can roll on items that match the `sieve` received."""
    mods: dict[str] = web.get(_URL, expiration=Expiration.MONTHLY, formatter=_format_mods)
    (domains, tags) = base.get_domains_and_tags(sieve)
    return {
        mod_info[NAME_FIELD]
        for mod_info in mods.values()
        if _is_mod_info_valid_to_return(mod_info, domains, tags, sieve) }

def _format_mods(mods_json: dict[str]):
    return {
        mod_key: mod_info
        for mod_key, mod_info in mods_json.items()
        if _is_mod_info_valid_to_format(mod_info) }

def _is_mod_info_valid_to_format(mod_info: dict[str]):
    return mod_info[NAME_FIELD] != "" and \
        mod_info[_GENERATION_TYPE_FIELD] in _VALID_GENERATION_TYPES

def _is_mod_info_valid_to_return(mod_info: dict[str], domains: set[str], tags: set[str], sieve: Sieve):
    if mod_info[DOMAIN_FIELD] not in domains:
        return False

    if { ITEM_LEVEL: mod_info[_REQUIRED_LEVEL_FIELD] } not in sieve:
        return False

    for weight in mod_info[_SPAWN_WEIGHTS_FIELD]:
        if weight[_WEIGHT_FIELD] > 0 and weight[_TAG_FIELD] in tags:
            return True

    return False