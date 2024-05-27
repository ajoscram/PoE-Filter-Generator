import web
from . import base
from web import Expiration
from core import Sieve, ITEM_LEVEL
from .constants import Field

_URL = "https://lvlvllvlvllvlvl.github.io/RePoE/mods.min.json"
_VALID_GENERATION_TYPES = [ "prefix", "suffix" ]

def get_mods(sieve: Sieve) -> set[str]:
    """Returns the names of mods that can roll on items that match the `sieve` received."""
    mods: dict[str] = web.get(_URL, Expiration.MONTHLY, formatter=_format_mods)
    (domains, tags) = base.get_domains_and_tags(sieve)
    return {
        mod_info[Field.NAME.value]
        for mod_info in mods.values()
        if _is_mod_info_valid_to_return(mod_info, domains, tags, sieve) }

def _format_mods(mods_json: dict[str]):
    return {
        mod_key: mod_info
        for mod_key, mod_info in mods_json.items()
        if _is_mod_info_valid_to_format(mod_info) }

def _is_mod_info_valid_to_format(mod_info: dict[str]):
    return mod_info[Field.NAME.value] != "" and \
        mod_info[Field.GENERATION_TYPE.value] in _VALID_GENERATION_TYPES

def _is_mod_info_valid_to_return(mod_info: dict[str], domains: set[str], tags: set[str], sieve: Sieve):
    if mod_info[Field.DOMAIN.value] not in domains:
        return False

    if { ITEM_LEVEL: mod_info[Field.REQUIRED_LEVEL.value] } not in sieve:
        return False

    for weight in mod_info[Field.SPAWN_WEIGHTS.value]:
        if weight[Field.WEIGHT.value] > 0 and weight[Field.TAG.value] in tags:
            return True

    return False