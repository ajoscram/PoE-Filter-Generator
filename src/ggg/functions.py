import web
from enum import Enum
from web import Expiration
from core import ExpectedError

_LEAGUES_URL = "https://api.pathofexile.com/leagues?type=main&realm=pc"
_LEAGUE_ID_FIELD = "id"

_LEAGUE_NOT_FOUND_ERROR = "Unable to resolve the name of the current {0} league. Ensure it is currently enabled in-game."
_ERROR_PART_SEPARATOR = ", "
_HARDCORE = "hardcore"
_STANDARD = "standard"
_RUTHLESS = "ruthless"
_TEMP = "temp"

class _LeagueIndex(Enum):
    STANDARD = 0
    HARDCORE_STANDARD = 1
    RUTHLESS_STANDARD = 4
    RUTHLESS_HARDCORE_STANDARD = 5
    SOFTCORE_TEMP = 8
    HARDCORE_TEMP = 9
    RUTHLESS_SOFTCORE_TEMP = 12
    RUTHLESS_HARDCORE_TEMP = 13

def get_league_name(standard: bool = False, hardcore: bool = False, ruthless: bool = False):
    """Gets a league's name from GGG's API depending on the variables passed in:
    * `standard`: `True` for standard, `False` for the current temp league.
    * `hardcore`: `True` for hardcore, `False` for softcore.
    * `ruthless`: `True` for ruthless, `False` for non-ruthless."""
    index = _get_league_index(standard, hardcore, ruthless)
    leagues = web.get(_LEAGUES_URL, Expiration.DAILY)
    if index.value >= len(leagues):
        error_message = _get_error_message(standard, hardcore, ruthless)
        raise ExpectedError(error_message)
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
        return _LeagueIndex.SOFTCORE_TEMP
    elif not standard and hardcore and not ruthless:
        return _LeagueIndex.HARDCORE_TEMP
    elif not standard and not hardcore and ruthless:
        return _LeagueIndex.RUTHLESS_SOFTCORE_TEMP
    elif not standard and hardcore and ruthless:
        return _LeagueIndex.RUTHLESS_HARDCORE_TEMP

def _get_error_message(standard: bool, hardcore: bool, ruthless: bool):
    message_parts = [ _STANDARD ] if standard else [ _TEMP ]
    if hardcore:
        message_parts += [ _HARDCORE ]
    if ruthless:
        message_parts += [ _RUTHLESS ]
    return _LEAGUE_NOT_FOUND_ERROR.format(_ERROR_PART_SEPARATOR.join(message_parts))