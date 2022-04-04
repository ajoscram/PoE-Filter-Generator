"""Handles creation of real-time economy modified subfilters.
Data is obtained via poe.ninja's API.
Hardcore standard is not supported because poe.ninja doesn't support it.

Usage:
    python generate.py input.filter [output.filter] .econ [hc | std]
Output:
    - output.filter
"""
import requests
from requests import ReadTimeout, ConnectTimeout, HTTPError, Timeout
from classes.generator_error import GeneratorError

from classes.section import Section
from classes.rule import Rule

NAME = "econ"
STANDARD_TAG = "std"
HARDCORE_TAG = "hc"
BASE_TYPE_IDENTIFIER = "BaseType"

POE_FILTER_GENERATOR_USER_AGENT = "PoE Filter Generator https://github.com/ajoscram/PoE-Filter-Generator/"
CURRENCY_API_URL = "https://poe.ninja/api/data/currencyoverview"
ITEM_API_URL = "https://poe.ninja/api/data/itemoverview"
LEAGUE_NAME_API_URL = "https://api.pathofexile.com/leagues?type=main&realm=pc"
LEAGUE_NAME_STANDARD_INDEX = 0
LEAGUE_NAME_TEMP_INDEX = 4
LEAGUE_NAME_TEMP_HC_INDEX = 5

ERROR_MESSAGE_PREFIX = "Error while getting the {0}.\n"
HTTP_ERROR_MESSAGE = ERROR_MESSAGE_PREFIX + "You might want to report this error to @ajoscram on Github with this text:\n\n{1}"
CONNECTION_ERROR_MESSAGE = ERROR_MESSAGE_PREFIX + "Please make sure you have an active internet connection."
RULE_PARAMETER_COUNT_ERROR_MESSAGE = "The .econ rule expects 2 or 3 paramaters in its description, got {0}."
RULE_TYPE_ERROR_MESSAGE = "The .econ rule expects a valid type, got '{0}'."
RULE_BOUNDS_ERROR_MESSAGE = "The .econ rule expects a lower and upper bound as numbers, got '{0}' and '{1}' respectively."

LEAGUE_NAMES_ERROR_TEXT = "league names from GGG's API"
POE_NINJA_DATA_ERROR_TEXT = "data from poe.ninja"

TYPES = {
    "cur":"Currency",
    "fra":"Fragment",
    "oil":"Oil",
    "inc":"Incubator",
    "sca":"Scarab",
    "fos":"Fossil",
    "res":"Resonator",
    "ess":"Essence",
    "div":"DivinationCard",
    "bea":"Beast",
    "wat":"Watchstone"
}

poe_ninja_cache = {}
current_league = None

def handle(_, section: Section, options: list):
    """Handles creation of economy adjusted filters.
    Hardcore standard is not supported because poe.ninja doesn't support it.
    Options: 
        - if 'hc' is passed then the hardcore temp league is queried, if not softcore
        - if 'std' is passed then standard is queried, if not temp league
    """
    for rule in section.get_rules(NAME):
        rule_parameters = __parse_rule_parameters__(rule)
        league = __get_league__(options)
        base_types = __get_base_types__(league, rule_parameters["type"], rule_parameters["lower"], rule_parameters["upper"])
        base_types_string = __get_base_types_string__(base_types)
        section.swap(BASE_TYPE_IDENTIFIER, base_types_string)
    return [ section ]

def __get_league__(options: list = []):
    global current_league
    try:
        if not current_league:
            headers = {'User-Agent': POE_FILTER_GENERATOR_USER_AGENT}
            response = requests.get(LEAGUE_NAME_API_URL, headers=headers)
            response.raise_for_status()
            leagues = response.json()
            if STANDARD_TAG in options:
                current_league = leagues[LEAGUE_NAME_STANDARD_INDEX]["id"]
            elif HARDCORE_TAG in options:
                current_league = leagues[LEAGUE_NAME_TEMP_HC_INDEX]["id"]
            else:
                current_league = leagues[LEAGUE_NAME_TEMP_INDEX]["id"]
        return current_league
    except HTTPError as error:
        raise GeneratorError(HTTP_ERROR_MESSAGE.format(LEAGUE_NAMES_ERROR_TEXT, error))
    except (ConnectTimeout, ReadTimeout, Timeout, requests.ConnectionError):
        raise GeneratorError(CONNECTION_ERROR_MESSAGE.format(LEAGUE_NAMES_ERROR_TEXT))

def __parse_rule_parameters__(rule: Rule):
    parts = rule.description.split()
    if(len(parts) < 2 or len(parts) > 3):
        raise GeneratorError(RULE_PARAMETER_COUNT_ERROR_MESSAGE.format(len(parts)), rule.line_number)
    try:
        if(len(parts) == 2):
            return {
                "type": TYPES[parts[0]],
                "lower": float(parts[1]),
                "upper": None
            }
        else:
            return {
                "type": TYPES[parts[0]],
                "lower": float(parts[1]),
                "upper": float(parts[2])
            }
    except KeyError:
        raise GeneratorError(RULE_TYPE_ERROR_MESSAGE.format(parts[0]), rule.line_number)
    except ValueError:
        raise GeneratorError(RULE_BOUNDS_ERROR_MESSAGE.format(parts[1], parts[2]), rule.line_number)

def __get_base_types__(league: str, type: str, lower: float, upper: float = None):
    poe_ninja_lines = __get_poe_ninja_lines__(league, type)    
    base_types = []
    for line in poe_ninja_lines:
        name_lookup = "currencyTypeName" if "chaosEquivalent" in line else "name"
        value = line["chaosEquivalent"] if "chaosEquivalent" in line else line["chaosValue"]
        if value >= lower and (not upper or value < upper):
            base_types.append(line[name_lookup])
    return base_types

def __get_poe_ninja_lines__(league: str, type: str):
    global poe_ninja_cache
    try:
        if type not in poe_ninja_cache:
            type_is_currency_or_frags = type == TYPES["cur"] or type == TYPES["fra"]
            url = CURRENCY_API_URL if type_is_currency_or_frags else ITEM_API_URL
            response = requests.get(url, params={"league": league, "type": type})
            response.raise_for_status()
            poe_ninja_cache[type] = response.json()["lines"]
        return poe_ninja_cache[type]
    except HTTPError as error:
        raise GeneratorError(HTTP_ERROR_MESSAGE.format(POE_NINJA_DATA_ERROR_TEXT, error))
    except (ConnectTimeout, ReadTimeout, Timeout, requests.ConnectionError):
        raise GeneratorError(CONNECTION_ERROR_MESSAGE.format(POE_NINJA_DATA_ERROR_TEXT))

def __get_base_types_string__(base_types):
    base_types_string = f"\t{BASE_TYPE_IDENTIFIER} =="
    for base in base_types:
        base_types_string += f" \"{base}\""
    return base_types_string