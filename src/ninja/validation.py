from typing import Callable
from core import Sieve, Operand
from .value_range import ValueRange
from .constants import QueryType, Field, UNIQUE_QUERY_TYPES

_REPLICA_ITEM_NAME_EXCEPTIONS = [ "Replica Dragonfang's Flight" ]

def get_validator(type: QueryType) -> Callable[[dict[str], ValueRange, Sieve], bool]:
    """Returns a function that receives a `record` dictionary, `ValueRange` and a `Sieve` to determine
    whether or not the `record` is valid."""
    match type:
        case QueryType.CURRENCY | QueryType.FRAGMENT:
            return _is_currency_valid
        case QueryType.GEM:
            return _is_gem_valid
        case x if x in UNIQUE_QUERY_TYPES:
            return _is_unique_valid
        case _:
            return _is_item_valid

def _is_currency_valid(record: dict[str], range: ValueRange, _):
    return record[Field.CURRENCY_VALUE] in range

def _is_unique_valid(record: dict[str], range: ValueRange, sieve: Sieve):
    unique_name: str = record[Field.NAME]
    is_replica = unique_name.startswith(f"{Operand.REPLICA} ") and unique_name not in _REPLICA_ITEM_NAME_EXCEPTIONS
    pattern = {
        Operand.CLASS: record[Field.CLASS],
        Operand.REPLICA: is_replica,
        Operand.LINKED_SOCKETS: record[Field.LINKS] \
            if Field.LINKS in record else 0 }
    return pattern in sieve and _is_item_valid(record, range, sieve)

def _is_gem_valid(record: dict[str], range: ValueRange, sieve: Sieve):
    pattern = {
        Operand.GEM_LEVEL: record[Field.GEM_LEVEL],
        Operand.QUALITY: record[Field.GEM_QUALITY] \
            if Field.GEM_QUALITY in record else 0,
        Operand.CORRUPTED: record[Field.CORRUPTED] \
            if Field.CORRUPTED in record else False }
    return pattern in sieve and _is_item_valid(record, range, sieve)

def _is_item_valid(record: dict[str], range: ValueRange, _):
    return record[Field.ITEM_VALUE_FIELD] in range