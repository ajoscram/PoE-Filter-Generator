import web
from web import Expiration
from .constants import Field, ROYALE_PATTERN
from .matchable import Matchable

_URL = "https://lvlvllvlvllvlvl.github.io/RePoE/gems.min.json"

def is_base_gem(metadata_id: str):
    """Returns `True` if the `metadata_id` received corresponds to a base gem. `False` otherwise."""
    for gem_info in _get_gems().values():
        id_matches = metadata_id == gem_info[Field.BASE_ITEM][Field.ID]
        is_gem_base = gem_info[Field.DISPLAY_NAME] == gem_info[Field.BASE_ITEM][Field.DISPLAY_NAME]
        if id_matches and is_gem_base:
            return True
    return False

def try_get_gem_base(name: str):
    """Returns the base gem name of a gem called `name`.
    - If `name` is itself a base gem name, then it is returned as is.
    - If `name` is not a gem name, `None` is returned."""
    gems = _get_gems()
    if name not in gems:
        return None

    return gems[name][Field.BASE_ITEM][Field.DISPLAY_NAME]

def _get_gems() -> dict[str]:
    return web.get(_URL, Expiration.MONTHLY, formatter=_format_gems_info)

def _format_gems_info(gems_json: dict[str, dict]):
    return {
        gem_info[Field.DISPLAY_NAME]: gem_info
        for gem_info in gems_json.values()
        if _is_gem_info_valid(gem_info) }

def _is_gem_info_valid(gem_info: dict[str]):
    if Field.BASE_ITEM not in gem_info:
        return False

    if Field.DISPLAY_NAME not in gem_info:
        return False

    return Matchable(gem_info[Field.BASE_ITEM][Field.ID]) != ROYALE_PATTERN