import ggg, ninja, utils
from core import GeneratorError, Block, Rule
from core.constants import BASE_TYPE, CONTAINS, EQUALS, GREATER, GREATER_EQUALS, LESS, LESS_EQUALS, LINKED_SOCKETS, REPLICA

NAME = "econ"

_STANDARD_OPTION = "std"
_HARDCORE_OPTION = "hc"
_RUTHLESS_OPTION = "rth"

_UNIQUE_MNEMONIC = "uni"
_CURRENCY_MNEMONICS = {
    "cur": ninja.CurrencyType.BASIC,
    "fra": ninja.CurrencyType.FRAGMENT,
}
_MISC_MNEMONICS = {
    "oil": ninja.MiscItemType.OIL,
    "inc": ninja.MiscItemType.INCUBATOR,
    "sca": ninja.MiscItemType.SCARAB,
    "fos": ninja.MiscItemType.FOSSIL,
    "res": ninja.MiscItemType.RESONATOR,
    "ess": ninja.MiscItemType.ESSENCE,
    "div": ninja.MiscItemType.DIVINATION_CARD,
    "bea": ninja.MiscItemType.BEAST,
    "inv": ninja.MiscItemType.INVITATION,
    "via": ninja.MiscItemType.VIAL,
    "del": ninja.MiscItemType.DELIRIUM_ORB,
}

_RULE_PARAMETER_COUNT_ERROR = "The .econ rule expects 2 or 3 paramaters in its description, got {0}."
_RULE_MNEMONIC_ERROR = "The .econ rule expects a valid type mnemonic, got '{0}'."
_RULE_BOUNDS_ERROR = "The .econ rule expects a numerical {0} bound, got '{1}'."
_LOWER_BOUND_NAME = "lower"
_UPPER_BOUND_NAME = "upper"

class _Params:
    def __init__(self, mnemonic: str, league_name: str, line_number: int, lower: float, upper: float = None):
        self.mnemonic = mnemonic
        self.league_name = league_name
        self.line_number = line_number
        self.lower = lower
        self.upper = upper

def handle(_, block: Block, options: list[str]):
    """Handles creation of economy adjusted filters.
    Hardcore standard is not supported because poe.ninja doesn't support it.
    Options:
        - if `hc` is passed hardcore leagues will be queried, otherwise softcore is queried instead
        - if `std` is passed then standard leagues will be queried, otherwise the temp league is queried instead
        - if `rth` is passed then ruthless leagues will be queried"""
    rules = block.get_rules(NAME)
    if len(rules) > 0:
        league_name = _get_league_name(options)
        base_types = []
        for rule in rules:
            params = _get_params(rule, league_name)
            base_types += _get_base_types(params, block)

        for line in block.find(operand=BASE_TYPE):
            line.operator = "=="
            line.values = [ f'"{base_type}"' for base_type in set(base_types) ]
        
        if len(base_types) == 0:
            block.comment_out()

    return block.get_raw_lines()

def _get_league_name(options: list[str]):
    standard = _STANDARD_OPTION in options
    hardcore = _HARDCORE_OPTION in options
    ruthless = _RUTHLESS_OPTION in options
    return ggg.get_league_name(standard, hardcore, ruthless)

def _get_params(rule: Rule, league_name: str):
    parts = rule.description.split()
    if len(parts) not in [2, 3]:
        raise GeneratorError(_RULE_PARAMETER_COUNT_ERROR.format(len(parts)), rule.line_number)
    
    if not parts[1].isdigit():
        raise GeneratorError(_RULE_BOUNDS_ERROR.format(_LOWER_BOUND_NAME, parts[1]), rule.line_number)
    lower = float(parts[1])

    if len(parts) == 3 and not parts[2].isdigit(): 
        raise GeneratorError(_RULE_BOUNDS_ERROR.format(_UPPER_BOUND_NAME, parts[2]), rule.line_number)
    upper = float(parts[2]) if len(parts) == 3 else None
 
    return _Params(parts[0], league_name, rule.line_number, lower, upper)

def _get_base_types(params: _Params, block: Block):
    if params.mnemonic in _CURRENCY_MNEMONICS:
        currency_type = _CURRENCY_MNEMONICS[params.mnemonic]
        return ninja.get_currency_base_types(params.league_name, currency_type, params.lower, params.upper)
    
    if params.mnemonic in _MISC_MNEMONICS:
        misc_type = _MISC_MNEMONICS[params.mnemonic]
        return ninja.get_misc_base_types(params.league_name, misc_type, params.lower, params.upper)
    
    if params.mnemonic == _UNIQUE_MNEMONIC:
        unique_filter = _get_unique_filter(block)
        return ninja.get_unique_base_types(params.league_name, unique_filter, params.lower, params.upper)

    raise GeneratorError(_RULE_MNEMONIC_ERROR.format(params.mnemonic), params.line_number)

def _get_unique_filter(block: Block):
    unique_filter = ninja.UniqueFilter()

    classes = block.get_classes()
    if len(classes) > 0:
        classes = [ utils.try_translate_class(class_) for class_ in classes ]
        unique_filter.classes = classes
    
    replica_lines = block.find(operand=REPLICA)
    if len(replica_lines) > 0:
        unique_filter.is_replica = replica_lines[-1].get_value_as_bool()

    equals_links = _get_equals_link_values(block)
    unique_filter.min_links = equals_links if equals_links != None else _get_min_links(block)
    unique_filter.max_links = equals_links if equals_links != None else _get_max_links(block)

    return unique_filter

def _get_min_links(block: Block):
    greater_than_or_equal_lines = block.find(operand=LINKED_SOCKETS, operator=GREATER_EQUALS)
    values = [ line.get_value_as_int() for line in greater_than_or_equal_lines ]
    
    greater_than_lines = block.find(operand=LINKED_SOCKETS, operator=GREATER)
    values += [ line.get_value_as_int() + 1 for line in greater_than_lines ]

    return min(values) if len(values) > 0 else None

def _get_max_links(block: Block):
    less_than_or_equal_lines = block.find(operand=LINKED_SOCKETS, operator=LESS_EQUALS)
    values = [ line.get_value_as_int() for line in less_than_or_equal_lines ]
    
    less_than_lines = block.find(operand=LINKED_SOCKETS, operator=LESS)
    values += [ line.get_value_as_int() - 1 for line in less_than_lines ]

    return max(values) if len(values) > 0 else None

def _get_equals_link_values(block: Block):
    empty_equals_lines = block.find(operand=LINKED_SOCKETS, operator="")
    equals_lines = block.find(operand=LINKED_SOCKETS, operator=CONTAINS)
    strict_equals_lines = block.find(operand=LINKED_SOCKETS, operator=EQUALS)
    values = [
        line.get_value_as_int()
        for line in empty_equals_lines + equals_lines + strict_equals_lines
    ]
    return max(values) if len(values) > 0 else None