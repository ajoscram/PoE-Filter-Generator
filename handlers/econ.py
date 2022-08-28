import requests
from requests import ReadTimeout, ConnectTimeout, HTTPError, Timeout
from classes.generator_error import GeneratorError

from classes.block import Block
from classes.rule import Rule

_NAME = "econ"
_STANDARD_TAG = "std"
_HARDCORE_TAG = "hc"
_BASE_TYPE_IDENTIFIER = "BaseType"

_FILTER_GENERATOR_USER_AGENT = "PoE Filter Generator https://github.com/ajoscram/PoE-Filter-Generator/"
_CURRENCY_API_URL = "https://poe.ninja/api/data/currencyoverview"
_ITEM_API_URL = "https://poe.ninja/api/data/itemoverview"
_LEAGUE_NAME_API_URL = "https://api.pathofexile.com/leagues?type=main&realm=pc"
_LEAGUE_NAME_STANDARD_INDEX = 0
_LEAGUE_NAME_TEMP_INDEX = 4
_LEAGUE_NAME_TEMP_HC_INDEX = 5

_ERROR_MESSAGE_PREFIX = "Error while getting the {0}.\n"
_HTTP_ERROR = _ERROR_MESSAGE_PREFIX + "You might want to report this error to @ajoscram on Github with this text:\n\n{1}"
_CONNECTION_ERROR = _ERROR_MESSAGE_PREFIX + "Please make sure you have an active internet connection."
_RULE_PARAMETER_COUNT_ERROR = "The .econ rule expects 2 or 3 paramaters in its description, got {0}."
_RULE_TYPE_ERROR = "The .econ rule expects a valid type, got '{0}'."
_RULE_BOUNDS_ERROR = "The .econ rule expects a numerical {0} bound, got '{1}'."

_LEAGUE_NAMES_ERROR_TEXT = "league names from GGG's API"
_NINJA_DATA_ERROR_TEXT = "data from poe.ninja"

_TYPES = {
    "cur": "Currency",
    "fra": "Fragment",
    "oil": "Oil",
    "inc": "Incubator",
    "sca": "Scarab",
    "fos": "Fossil",
    "res": "Resonator",
    "ess": "Essence",
    "div": "DivinationCard",
    "bea": "Beast",
    "inv": "Invitation",
    "via": "Vial",
    "del": "DeliriumOrb"
}

class _Params:
    def __init__(self, type: str, lower: float, upper: float = None):
        self.type = type
        self.lower = lower
        self.upper = upper
        self.ninja_url = self._get_ninja_url(type)
    
    def _get_ninja_url(self, type: str):
        if type == _TYPES["cur"] or type == _TYPES["fra"]:
            return _CURRENCY_API_URL
        else:
            return _ITEM_API_URL

_ninja_cache = {}
_league = None

def handle(_, block: Block, options: list):
    """Handles creation of economy adjusted filters.
    Hardcore standard is not supported because poe.ninja doesn't support it.
    Options: 
        - if 'hc' is passed then the hardcore temp league is queried, if not softcore
        - if 'std' is passed then standard is queried, if not temp league"""
    for rule in block.get_rules(_NAME):
        params = _parse_rule_params(rule)
        league = _get_league(options)
        base_types = _get_base_types(league, params)
        base_types_string = _get_base_types_string(base_types)
        block.swap(_BASE_TYPE_IDENTIFIER, base_types_string)
        if len(base_types) == 0:
            block.comment()
    return [ block ]

def _parse_rule_params(rule: Rule):
    parts = rule.description.split()
    if len(parts) < 2 or len(parts) > 3:
        raise GeneratorError(_RULE_PARAMETER_COUNT_ERROR.format(len(parts)), rule.line_number)
    
    if parts[0] not in _TYPES:
        raise GeneratorError(_RULE_TYPE_ERROR.format(parts[0]), rule.line_number)
    type = _TYPES[parts[0]]

    if not _is_float(parts[1]): 
        raise GeneratorError(_RULE_BOUNDS_ERROR.format("lower", parts[1]), rule.line_number)
    lower = float(parts[1])

    if len(parts) == 3 and not _is_float(parts[2]): 
        raise GeneratorError(_RULE_BOUNDS_ERROR.format("upper", parts[2]), rule.line_number)
    upper = float(parts[2]) if len(parts) == 3 else None

    return _Params(type, lower, upper)

def _is_float(string: str):
    try:
        float(string)
        return True
    except ValueError:
        return False

def _get_league(options: list[str]):
    global _league
    try:
        if _league == None:
            headers = {'User-Agent': _FILTER_GENERATOR_USER_AGENT}
            response = requests.get(_LEAGUE_NAME_API_URL, headers=headers)
            response.raise_for_status()
            leagues = response.json()
            if _STANDARD_TAG in options:
                _league = leagues[_LEAGUE_NAME_STANDARD_INDEX]["id"]
            elif _HARDCORE_TAG in options:
                _league = leagues[_LEAGUE_NAME_TEMP_HC_INDEX]["id"]
            else:
                _league = leagues[_LEAGUE_NAME_TEMP_INDEX]["id"]
        return _league
    except HTTPError as error:
        raise GeneratorError(_HTTP_ERROR.format(_LEAGUE_NAMES_ERROR_TEXT, error))
    except (ConnectTimeout, ReadTimeout, Timeout, requests.ConnectionError):
        raise GeneratorError(_CONNECTION_ERROR.format(_LEAGUE_NAMES_ERROR_TEXT))

def _get_base_types(league: str, params: _Params):
    lines = _get_ninja_lines(params.ninja_url, league, params.type)
    base_types = []
    for line in lines:
        value = line["chaosEquivalent"] if "chaosEquivalent" in line else line["chaosValue"]
        name_lookup = "currencyTypeName" if "chaosEquivalent" in line else "name"
        base_type = line[name_lookup]
        if _is_base_type_valid(base_type) and _is_value_valid(value, params):
            base_types.append(base_type)
    return base_types

def _get_ninja_lines(url: str, league: str, type: str):
    global _ninja_cache
    try:
        if type not in _ninja_cache:
            response = requests.get(url, params={"league": league, "type": type})
            response.raise_for_status()
            _ninja_cache[type] = response.json()["lines"]
        return _ninja_cache[type]
    except HTTPError as error:
        raise GeneratorError(_HTTP_ERROR.format(_NINJA_DATA_ERROR_TEXT, error))
    except (ConnectTimeout, ReadTimeout, Timeout, requests.ConnectionError):
        raise GeneratorError(_CONNECTION_ERROR.format(_NINJA_DATA_ERROR_TEXT))

def _get_base_types_string(base_types):
    base_types_string = f"\t{_BASE_TYPE_IDENTIFIER} =="
    for base in base_types:
        base_types_string += f" \"{base}\""
    return base_types_string

def _is_value_valid(value: float, params: _Params):
    return value >= params.lower and (params.upper == None or value < params.upper)

def _is_base_type_valid(base_type: str):
    '''Removes poe.ninja entries which are not BaseTypes.'''
    if base_type in ["Will of Chaos", "Ignominious Fate", "Victorious Fate", "Deadly End"]:
        return False
    else:
        return True