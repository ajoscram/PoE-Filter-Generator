"""Handles creation of real-time economy modified subfilters.
Data is obtained via poe.ninja's API. Hardcore standard is not supported because poe.ninja doesn't support it.

Usage:
    python generate.py input.filter [output.filter] .econ [hc]
Output:
    - output.filter
"""
import os, requests

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
        - the price upper bound to look for in chaos, exclusive
    Returns a dictionary that looks like this:
        {type: string, lower: number, upper: number}
    """
    parts = rule.description.split()
    if(len(parts) != 3):
        raise HandlerError(rule.line_number, "The .econ rule expects 3 paramaters in its description, got "+str(len(parts))+".")
    try:
        return {
            "type": TYPES[parts[0]],
            "lower": float(parts[1]),
            "upper": float(parts[2])
        }
    except KeyError:
        raise HandlerError(rule.line_number, "The .econ rule expects a valid type, got '" + parts[0]+"'.")
    except ValueError:
        raise HandlerError(rule.line_number, "The .econ rule expects a lower and upper bound as numbers, got '" + parts[1] + "' and '" + parts[2]+"' respectively.")

def __get_base_types__(league: str, type_: str, lower: float, upper: float, cache: dict = {}):
    """Fetches all BaseType item names needed
    """
    try:
        #get the lines list with every base type and their prices
        lines = []
        if cache.has_key(type_):
            lines = cache[type_]["lines"]
        else:
            response = requests.get(ITEM_API_LINK, params={"league": league, "type": type_})
            response.raise_for_status()
            lines = response.json()["lines"]
            cache[type_] = lines
        #go through every line and add every base which is inside the bound
        bases = []
        for line in lines:
            
            name_lookup = None
            value = None
            
            if line.has_key("chaosEquivalent"):
                value = line["chaosEquivalent"]
                name_lookup = "currencyTypeName"
            else:
                value = line["chaosValue"]
                name_lookup = "name"
            
            if value >= lower and value < upper:
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
    league = __get_league__(options)
    filter_file = open(filepath, 'w+')
    cache = {}
    for section in sections:
        for rule in section.rules:
            if rule.tag == TAG:
                params = __parse__(rule)
                bases = __get_base_types__(league, params["type"], params["lower"], params["upper"], cache)
                #do the actual swap of base types
        for line in section.lines:
            filter_file.write(line + '\n')
    filter_file.close()