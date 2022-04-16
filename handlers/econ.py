import requests
from requests import ReadTimeout, ConnectTimeout, HTTPError, Timeout
from classes.generator_error import GeneratorError

from classes.block import Block
from classes.rule import Rule

_NAME = "econ"
_STANDARD_TAG = "std"
_HARDCORE_TAG = "hc"
_BASE_TYPE_IDENTIFIER = "BaseType"

_POE_FILTER_GENERATOR_USER_AGENT = "PoE Filter Generator https://github.com/ajoscram/PoE-Filter-Generator/"
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
_RULE_BOUNDS_ERROR = "The .econ rule expects a lower and upper bound as numbers, got '{0}' and '{1}' respectively."

_LEAGUE_NAMES_ERROR_TEXT = "league names from GGG's API"
_POE_NINJA_DATA_ERROR_TEXT = "data from poe.ninja"

_TYPES = {
    "cur":"Currency",
    "fra":"Fragment",
    "oil":"Oil",
    "inc":"Incubator",
    "sca":"Scarab",
    "fos":"Fossil",
    "res":"Resonator",
    "ess":"Essence",
    "div":"DivinationCard",
    "bea":"Beast"
}

_poe_ninja_cache = {}
_current_league = None

def handle(_, block: Block, options: list):
    """Handles creation of economy adjusted filters.
    Hardcore standard is not supported because poe.ninja doesn't support it.
    Options: 
        - if 'hc' is passed then the hardcore temp league is queried, if not softcore
        - if 'std' is passed then standard is queried, if not temp league"""
    for rule in block.get_rules(_NAME):
        params = _parse_rule_params(rule)
        league = _get_league(options)
        base_types = _get_base_types(league, params["type"], params["lower"], params["upper"])
        base_types_string = _get_base_types_string(base_types)
        block.swap(_BASE_TYPE_IDENTIFIER, base_types_string)
    return [ block ]

def _get_league(options: list[str]):
    global _current_league
    try:
        if not _current_league:
            headers = {'User-Agent': _POE_FILTER_GENERATOR_USER_AGENT}
            response = requests.get(_LEAGUE_NAME_API_URL, headers=headers)
            response.raise_for_status()
            leagues = response.json()
            if _STANDARD_TAG in options:
                _current_league = leagues[_LEAGUE_NAME_STANDARD_INDEX]["id"]
            elif _HARDCORE_TAG in options:
                _current_league = leagues[_LEAGUE_NAME_TEMP_HC_INDEX]["id"]
            else:
                _current_league = leagues[_LEAGUE_NAME_TEMP_INDEX]["id"]
        return _current_league
    except HTTPError as error:
        raise GeneratorError(_HTTP_ERROR.format(_LEAGUE_NAMES_ERROR_TEXT, error))
    except (ConnectTimeout, ReadTimeout, Timeout, requests.ConnectionError):
        raise GeneratorError(_CONNECTION_ERROR.format(_LEAGUE_NAMES_ERROR_TEXT))

def _parse_rule_params(rule: Rule):
    parts = rule.description.split()
    if len(parts) < 2 or len(parts) > 3:
        raise GeneratorError(_RULE_PARAMETER_COUNT_ERROR.format(len(parts)), rule.line_number)
    try:
        if len(parts) == 2:
            return {
                "type": _TYPES[parts[0]],
                "lower": float(parts[1]),
                "upper": None
            }
        else:
            return {
                "type": _TYPES[parts[0]],
                "lower": float(parts[1]),
                "upper": float(parts[2])
            }
    except KeyError:
        raise GeneratorError(_RULE_TYPE_ERROR.format(parts[0]), rule.line_number)
    except ValueError:
        raise GeneratorError(_RULE_BOUNDS_ERROR.format(parts[1], parts[2]), rule.line_number)

def _get_base_types(league: str, type: str, lower: float, upper: float = None):
    poe_ninja_lines = _get_poe_ninja_lines(league, type)    
    base_types = []
    for line in poe_ninja_lines:
        name_lookup = "currencyTypeName" if "chaosEquivalent" in line else "name"
        value = line["chaosEquivalent"] if "chaosEquivalent" in line else line["chaosValue"]
        if value >= lower and (not upper or value < upper):
            base_types.append(line[name_lookup])
    return base_types

def _get_poe_ninja_lines(league: str, type: str):
    global _poe_ninja_cache
    try:
        if type not in _poe_ninja_cache:
            type_is_currency_or_frags = type == _TYPES["cur"] or type == _TYPES["fra"]
            url = _CURRENCY_API_URL if type_is_currency_or_frags else _ITEM_API_URL
            response = requests.get(url, params={"league": league, "type": type})
            response.raise_for_status()
            _poe_ninja_cache[type] = response.json()["lines"]
        return _poe_ninja_cache[type]
    except HTTPError as error:
        raise GeneratorError(_HTTP_ERROR.format(_POE_NINJA_DATA_ERROR_TEXT, error))
    except (ConnectTimeout, ReadTimeout, Timeout, requests.ConnectionError):
        raise GeneratorError(_CONNECTION_ERROR.format(_POE_NINJA_DATA_ERROR_TEXT))

def _get_base_types_string(base_types):
    base_types_string = f"\t{_BASE_TYPE_IDENTIFIER} =="
    for base in base_types:
        base_types_string += f" \"{base}\""
    return base_types_string