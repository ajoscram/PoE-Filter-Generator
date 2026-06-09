import web
from web import Expiration
from core import ExpectedError
from .constants import Field

_URL = "https://repoe-fork.github.io/cluster_jewels.json"

_ENCHANT_NOT_FOUND_ERROR = """A cluster jewel enchantment with the stat '{0}' could not be found when attempting to get its name.

\tThis problem is likely solved by deleting PFG's cache with the command [cyan]pfg -clean[/cyan]."""

_CLUSTER_FIELDS = [ Field.LARGE_CLUSTER, Field.MEDIUM_CLUSTER, Field.SMALL_CLUSTER ]

def get_cluster_enchant(stat_text: str):
    jewels_info = web.get(_URL, Expiration.MONTHLY)

    for cluster_field in _CLUSTER_FIELDS:
        if enchant := _try_get_enchant(stat_text, jewels_info[cluster_field]):
            return enchant
    
    raise ExpectedError(_ENCHANT_NOT_FOUND_ERROR.format(stat_text))

def _try_get_enchant(stat_text: str, jewel_info: dict[str]):
    for passive_skill in jewel_info[Field.PASSIVE_SKILLS]:
        if stat_text in passive_skill[Field.STAT_TEXT]:
            return passive_skill[Field.NAME]
    
    return None