import repoe
from core import Block, Sieve, ExpectedError, Operand

NAME = "game"

_MOD_PARAM = "mod"
_BASE_PARAM = "base"

_INVALID_PARAM_ERROR = "'{0}' is not a valid parameter for the .game rule."

def handle(block: Block, _):
    """Updates lines within blocks with in-game information."""
    params = {
        param: rule.line_number
        for rule in reversed(block.get_rules(NAME))
        for param in rule.description.split() }
    
    for param, line_number in params.items():
        operand, values = _get_operand_and_values(param, block.get_sieve(), line_number)
        block.upsert(operand, [ f'"{value}"' for value in values ])

    return block.get_raw_lines()

def _get_operand_and_values(param: str, sieve: Sieve, line_number: int):
    if param == _MOD_PARAM:
        return (Operand.HAS_EXPLICIT_MOD, repoe.get_mods(sieve))
    
    if param == _BASE_PARAM:
        return (Operand.BASE_TYPE, repoe.get_bases(sieve))
    
    raise ExpectedError(_INVALID_PARAM_ERROR.format(param), line_number)