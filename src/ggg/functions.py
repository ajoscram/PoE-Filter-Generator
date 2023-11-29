import web
from enum import Enum

_LEAGUES_URL = "https://api.pathofexile.com/leagues?type=main&realm=pc"
_LEAGUE_ID_FIELD = "id"

class _LeagueIndex(Enum):
    STANDARD = 0
    HARDCORE_STANDARD = 1
    RUTHLESS_STANDARD = 4
    RUTHLESS_HARDCORE_STANDARD = 5
    TEMP_SOFTCORE = 8
    TEMP_HARDCORE = 9
    RUTHLESS_SOFTCORE = 12
    RUTHLESS_HARDCORE = 13

def get_league_name(standard: bool = False, hardcore: bool = False, ruthless: bool = False):
    """Gets a league's name from GGG's API depending on the variables passed in:
    * `standard`: `True` for standard, `False` for the current temp league.
    * `hardcore`: `True` for hardcore, `False` for softcore.
    * `ruthless`: `True` for ruthless, `False` for non-ruthless."""
    index = _get_league_index(standard, hardcore, ruthless)
    leagues = web.get(_LEAGUES_URL, expiration=web.Expiration.DAILY)
    return leagues[index.value][_LEAGUE_ID_FIELD]

def _get_league_index(standard: bool, hardcore: bool, ruthless: bool):
    if standard and not hardcore and not ruthless:
        return _LeagueIndex.STANDARD
    elif standard and hardcore and not ruthless:
        return _LeagueIndex.HARDCORE_STANDARD
    elif standard and not hardcore and ruthless:
        return _LeagueIndex.RUTHLESS_STANDARD
    elif standard and hardcore and ruthless:
        return _LeagueIndex.RUTHLESS_HARDCORE_STANDARD
    elif not standard and not hardcore and not ruthless:
        return _LeagueIndex.TEMP_SOFTCORE
    elif not standard and hardcore and not ruthless:
        return _LeagueIndex.TEMP_HARDCORE
    elif not standard and not hardcore and ruthless:
        return _LeagueIndex.RUTHLESS_SOFTCORE
    elif not standard and hardcore and ruthless:
        return _LeagueIndex.RUTHLESS_HARDCORE