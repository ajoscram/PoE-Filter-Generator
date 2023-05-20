import utils

_LEAGUES_URL = "https://api.pathofexile.com/leagues?type=main&realm=pc"
_LEAGUES_ERROR_DESCRIPTOR = "leagues from GGG's API"
_LEAGUE_ID_FIELD = "id"

def get_league_name(standard: bool = False, hardcore: bool = False, ruthless: bool = False):
    """Gets a league's name from GGG's API depending on the variables passed in:
    * `standard`: `True` for standard, `False` for the current temp league.
    * `hardcore`: `True` for hardcore, `False` for softcore.
    * `ruthless`: `True` for ruthless, `False` for non-ruthless."""
    index = _get_league_index(standard, hardcore, ruthless)
    leagues = utils.http_get(_LEAGUES_URL, _LEAGUES_ERROR_DESCRIPTOR)
    return leagues[index][_LEAGUE_ID_FIELD]

def _get_league_index(standard: bool, hardcore: bool, ruthless: bool):
    if standard and not hardcore and not ruthless:
        return 0
    elif standard and hardcore and not ruthless:
        return 1
    elif standard and not hardcore and ruthless:
        return 4
    elif standard and hardcore and ruthless:
        return 5
    elif not standard and not hardcore and not ruthless:
        return 8
    elif not standard and hardcore and not ruthless:
        return 9
    elif not standard and not hardcore and ruthless:
        return 12
    elif not standard and hardcore and ruthless:
        return 13