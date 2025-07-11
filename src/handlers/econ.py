import ggg, ninja
from core import ExpectedError, Block, Rule, Sieve, Operand
from ninja import QueryType, ValueRange, UNIQUE_QUERY_TYPES
from .context import Context

NAME = "econ"

_STANDARD_OPTION = "std"
_HARDCORE_OPTION = "hc"
_RUTHLESS_OPTION = "rth"

_RULE_PARAMETER_COUNT_ERROR = "The .econ rule expects 2 or 3 paramaters in its description, got {0}."
_RULE_MNEMONIC_ERROR = "The .econ rule expects a valid type mnemonic, got '{0}'."
_RULE_BOUNDS_ERROR = "The .econ rule expects a numerical {0} bound, got '{1}'."
_LOWER_BOUND_NAME = "lower"
_UPPER_BOUND_NAME = "upper"

_QUERY_TYPES_BY_MNEMONIC: dict[str, set[QueryType]] = {
    "cur": { QueryType.CURRENCY },
    "fra": { QueryType.FRAGMENT },
    "gem": { QueryType.GEM },
    "oil": { QueryType.OIL },
    "inc": { QueryType.INCUBATOR },
    "sca": { QueryType.SCARAB },
    "fos": { QueryType.FOSSIL },
    "res": { QueryType.RESONATOR },
    "ess": { QueryType.ESSENCE },
    "div": { QueryType.DIVINATION_CARD },
    "inv": { QueryType.INVITATION },
    "via": { QueryType.VIAL },
    "del": { QueryType.DELIRIUM_ORB },
    "tat": { QueryType.TATTOO },
    "omn": { QueryType.OMEN },
    "mbr": { QueryType.ALLFLAME_EMBER },
    "run": { QueryType.RUNEGRAFT },
    "uni": UNIQUE_QUERY_TYPES,
}

class _Params:
    def __init__(self, query_types: set[QueryType], league_name: str, value_range: ValueRange):
        self.query_types = query_types
        self.league_name = league_name
        self.value_range = value_range

def handle(block: Block, context: Context):
    """Handles creation of economy adjusted filters.
    Options:
    - if `hc` is passed hardcore leagues will be queried, otherwise softcore is queried instead.
    - if `std` is passed then standard leagues will be queried, otherwise the temp league is queried instead.
    - if `rth` is passed then ruthless leagues will be queried."""
    rules = block.get_rules(NAME)
    if len(rules) > 0:

        bases = [ f'"{base}"' for base in _get_bases(rules, block.get_sieve(), context) ]
        if len(bases) > 0:
            block.upsert(Operand.BASE_TYPE, bases)
        else:
            block.comment_out()

    return block.get_raw_lines()

def _get_league_name(options: list[str]):
    standard = _STANDARD_OPTION in options
    hardcore = _HARDCORE_OPTION in options
    ruthless = _RUTHLESS_OPTION in options
    return ggg.get_league_name(standard, hardcore, ruthless)

def _get_bases(rules: list[Rule], sieve: Sieve, context: Context):
    bases: list[str] = []
    league_name = _get_league_name(context.options)

    for rule in rules:
        params = _get_params(rule, league_name)

        for query_type in params.query_types:
            bases += ninja.get_bases(query_type, params.league_name, sieve, params.value_range)

    return bases

def _get_params(rule: Rule, league_name: str):
    parts = rule.description.split()
    if len(parts) not in [2, 3]:
        raise ExpectedError(_RULE_PARAMETER_COUNT_ERROR.format(len(parts)), rule.line_number)
    
    mnemonic = parts[0]
    if mnemonic not in _QUERY_TYPES_BY_MNEMONIC:
        raise ExpectedError(_RULE_MNEMONIC_ERROR.format(mnemonic), rule.line_number)
    query_types = _QUERY_TYPES_BY_MNEMONIC[mnemonic]

    if not parts[1].isdigit():
        raise ExpectedError(_RULE_BOUNDS_ERROR.format(_LOWER_BOUND_NAME, parts[1]), rule.line_number)
    lower = float(parts[1])

    if len(parts) == 3 and not parts[2].isdigit(): 
        raise ExpectedError(_RULE_BOUNDS_ERROR.format(_UPPER_BOUND_NAME, parts[2]), rule.line_number)
    upper = float(parts[2]) if len(parts) == 3 else None
 
    return _Params(query_types, league_name, ValueRange(lower, upper))