"""Handles creation of real-time economy modified subfilters.
Data is obtained via poe.ninja's API. Hardcore standard is not supported because poe.ninja doesn't support it.

Usage:
    python generate.py input.filter [output.filter] .econ [hc]
Output:
    - output.filter
"""
import requests

from requests import ReadTimeout, ConnectTimeout, HTTPError, Timeout, ConnectionError
from classes.section import Section
from classes.rule import Rule
from classes.handler_error import HandlerError

TAG = "econ"
STANDARD_TAG = "std"
HARDCORE_TAG = "hc"
LEAGUE_NAME_API_URL = "https://api.pathofexile.com/leagues?type=main&realm=pc"
LEAGUE_NAME_STANDARD_INDEX = 0
LEAGUE_NAME_TEMP_INDEX = 4
LEAGUE_NAME_TEMP_HC_INDEX = 5
ITEM_API_URL = "https://poe.ninja/api/data/itemoverview"
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
    "pro":"Prophecy",
    "bea":"Beasts"
}

def __get_league__(options: list = []):
    """Returns the current temporal softcore league name as a string.
    If 'std' is passed as an option then the standard league name is returned.
    If 'hc' is passed as an option then the hardcore temporal league name is returned.
    Note that Hardcore Standard is not supported because poe.ninja doesn't support it.
    """
    try:
        response = requests.get(LEAGUE_NAME_API_URL)
        response.raise_for_status()
        leagues = response.json()
        if STANDARD_TAG in options:
            return leagues[LEAGUE_NAME_STANDARD_INDEX]["id"]
        elif HARDCORE_TAG in options:
            return leagues[LEAGUE_NAME_TEMP_HC_INDEX]["id"]
        else:
            return leagues[LEAGUE_NAME_TEMP_INDEX]["id"]
    except HTTPError as error:
        raise HandlerError(None, f"Error while getting the league names from GGG's API.\nYou might wanna report this error to @ajoscram on github or twitter with this text:\n\n{error}")
    except (ConnectTimeout, ReadTimeout, Timeout, requests.ConnectionError):
        raise HandlerError(None, "Error while getting the league names from GGG's API.\nPlease make sure you have an active internet connection.")

def __parse__(rule: Rule):
    """Parses the description string from a rule into three components:
        - the item type to query for in poe.ninja (defined in the TYPES dictionary)
        - the price lower bound to look for in chaos, inclusive
        - the price upper bound to look for in chaos, exclusive (optional)
    Returns a dictionary that looks like this:
        {type: string, lower: number, upper: number}
    """
    parts = rule.description.split()
    if(len(parts) < 2 or len(parts) > 3):
        raise HandlerError(rule.line_number, "The .econ rule expects 2 or 3 paramaters in its description, got "+str(len(parts))+".")
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
        raise HandlerError(rule.line_number, "The .econ rule expects a valid type, got '" + parts[0]+"'.")
    except ValueError:
        raise HandlerError(rule.line_number, "The .econ rule expects a lower and upper bound as numbers, got '" + parts[1] + "' and '" + parts[2]+"' respectively.")

def __get_base_types__(league: str, type_: str, lower: float, upper: float = None, cache: dict = {}):
    """Fetches all BaseType item names from PoE Ninja's API, for a particular league and item type.
    The items must also be greater than or equal to the lower bound, and optionally an upper bound can be passed. The uppper bound is excluded.
    The cache parameter is a dictionary which will be looked up for repeated requests instead of re-requesting, so it will be mutated.
    """
    try:
        #get the lines list from poe.ninja's API with every base type and their prices
        #if it's already in the cache use that instead
        lines = []
        if type_ in cache:
            lines = cache[type_]
        else:
            response = requests.get(ITEM_API_URL, params={"league": league, "type": type_})
            response.raise_for_status()
            lines = response.json()["lines"]
            cache[type_] = lines
        #go through every line and get every base which is inside the bound
        bases = []
        for line in lines:
            #get the base type's name and price
            name_lookup = None
            value = None
            if "chaosEquivalent" in line:
                value = line["chaosEquivalent"]
                name_lookup = "currencyTypeName"
            else:
                value = line["chaosValue"]
                name_lookup = "name"
            #finally if it's between the lower and upper bounds add it to the list
            if value >= lower and (not upper or (upper and value < upper)):
                bases.append(line[name_lookup])
        return bases
    except HTTPError as error:
        raise HandlerError(None, f"Error while getting data from poe.ninja.\nYou might wanna report this error to @ajoscram on github or twitter with this text:\n\n{error}")
    except (ConnectTimeout, ReadTimeout, Timeout, requests.ConnectionError):
        raise HandlerError(None, "Error while getting data from poe.ninja.\nPlease make sure you have an active internet connection.")

def handle(filepath:str, sections: list, options:list = []):
    """Handles creation of economy adjusted filters. This function is always called by a Generator object.
    Hardcore standard is not supported because poe.ninja doesn't support it.

    Arguments:
        filepath: filepath where the filter should be output to
        sections: list of Section objects which represent the input file
        options: 
            - if 'hc' is passed then the hardcore temp league is queried, if not softcore
            - if 'std' is passed then standard is queried, if not temp league
    """
    #get the selected league name
    league = __get_league__(options)
    filter_file = open(filepath, 'w+')
    #create a cache for repeated requests
    cache = {}
    for section in sections:
        for rule in section.rules:
            if rule.tag == TAG:
                #get the parameters from the rule's description
                params = __parse__(rule)
                #fetch the list of bases for those parameters
                bases = __get_base_types__(league, params["type"], params["lower"], params["upper"], cache)
                #create the string to swap into
                bases_string = "\tBaseType"
                for base in bases:
                    bases_string += " \"" + base + "\""
                #do the actual swap of base types
                section.swap("BaseType", bases_string)
        for line in section.lines:
            filter_file.write(line + '\n')
    filter_file.close()