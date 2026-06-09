import ggg, ninja
from dataclasses import dataclass
from core import ExpectedError, Block, Rule, Sieve, Operand
from ninja import BaseQueryType, ValueRange
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

_UNIQUE_BASE_QUERY_TYPES = {
    BaseQueryType.UNIQUE_ACCESSORY, \
    BaseQueryType.UNIQUE_ARMOUR, \
    BaseQueryType.UNIQUE_JEWEL, \
    BaseQueryType.UNIQUE_FLASK, \
    BaseQueryType.UNIQUE_MAP, \
    BaseQueryType.UNIQUE_WEAPON, \
    BaseQueryType.UNIQUE_RELIC, \
    BaseQueryType.UNIQUE_TINCTURE,
}

_CLUSTER_JEWEL_ENCHANT_MNEMONIC = "clj"

_BASE_QUERY_TYPES_BY_MNEMONIC: dict[str, set[BaseQueryType]] = {
    "cur": { BaseQueryType.CURRENCY },
    "fra": { BaseQueryType.FRAGMENT },
    "gem": { BaseQueryType.GEM },
    "oil": { BaseQueryType.OIL },
    "inc": { BaseQueryType.INCUBATOR },
    "sca": { BaseQueryType.SCARAB },
    "fos": { BaseQueryType.FOSSIL },
    "res": { BaseQueryType.RESONATOR },
    "ess": { BaseQueryType.ESSENCE },
    "div": { BaseQueryType.DIVINATION_CARD },
    "inv": { BaseQueryType.INVITATION },
    "via": { BaseQueryType.VIAL },
    "del": { BaseQueryType.DELIRIUM_ORB },
    "tat": { BaseQueryType.TATTOO },
    "omn": { BaseQueryType.OMEN },
    "mbr": { BaseQueryType.ALLFLAME_EMBER },
    "run": { BaseQueryType.RUNEGRAFT },
    "ast": { BaseQueryType.ASTROLABE },
    "dji": { BaseQueryType.DJINN_COIN },
    "art": { BaseQueryType.RUNIC_ARTIFACT },
    "wom": { BaseQueryType.WOMBGIFT },
    "uni": _UNIQUE_BASE_QUERY_TYPES,
}

@dataclass
class _Params:
    mnemonic: str
    league_name: str
    value_range: ValueRange
    line_number: int

def handle(block: Block, context: Context):
    """Handles creation of economy adjusted filters.
    Options:
    - if `hc` is passed hardcore leagues will be queried, otherwise softcore is queried instead.
    - if `std` is passed then standard leagues will be queried, otherwise the temp league is queried instead.
    - if `rth` is passed then ruthless leagues will be queried."""
    sieve = block.get_sieve()
    league_name = _get_league_name(context.options)
    params_list = [ _get_params(rule, league_name) for rule in block.get_rules(NAME) ]

    operands_and_values = [ _get_operand_and_values(params, sieve) for params in params_list ]
    for (operand, values) in operands_and_values:
        block.upsert(operand, [ f'"{value}"' for value in values ])

    if any(len(values) == 0 for (_, values) in operands_and_values):
        block.comment_out()

    return block.get_raw_lines()

def _get_operand_and_values(params: _Params, sieve: Sieve):    
    if params.mnemonic in _BASE_QUERY_TYPES_BY_MNEMONIC:
        return (Operand.BASE_TYPE, _get_base_types(params, sieve))

    if params.mnemonic == _CLUSTER_JEWEL_ENCHANT_MNEMONIC:
        return (Operand.ENCHANTMENT_PASSIVE_NODE,
            ninja.get_cluster_enchants(params.league_name, sieve, params.value_range))

    raise ExpectedError(_RULE_MNEMONIC_ERROR.format(params.mnemonic), params.line_number)

def _get_base_types(params: _Params, sieve: Sieve):
    return { base
        for query_type in _BASE_QUERY_TYPES_BY_MNEMONIC[params.mnemonic]
        for base in ninja.get_base_types(
            query_type, params.league_name, sieve, params.value_range) }

def _get_league_name(options: list[str]):
    standard = _STANDARD_OPTION in options
    hardcore = _HARDCORE_OPTION in options
    ruthless = _RUTHLESS_OPTION in options
    return ggg.get_league_name(standard, hardcore, ruthless)

def _get_params(rule: Rule, league_name: str):
    parts = rule.description.split()
    if len(parts) not in [2, 3]:
        raise ExpectedError(_RULE_PARAMETER_COUNT_ERROR.format(len(parts)), rule.line_number)

    mnemonic = parts[0]

    if not parts[1].isdigit():
        raise ExpectedError(_RULE_BOUNDS_ERROR.format(_LOWER_BOUND_NAME, parts[1]), rule.line_number)
    lower = float(parts[1])

    if len(parts) == 3 and not parts[2].isdigit(): 
        raise ExpectedError(_RULE_BOUNDS_ERROR.format(_UPPER_BOUND_NAME, parts[2]), rule.line_number)
    upper = float(parts[2]) if len(parts) == 3 else None
 
    return _Params(mnemonic, league_name, ValueRange(lower, upper), rule.line_number)