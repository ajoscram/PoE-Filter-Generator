from typing import Callable
from core import Sieve, REPLICA, LINKED_SOCKETS, CLASS, ITEM_LEVEL, CORRUPTED, QUALITY, GEM_LEVEL
from .value_range import ValueRange
from .constants import *

_INVALID_FRAGMENT_BASE_TYPES = [ "Will of Chaos", "Ignominious Fate", "Victorious Fate", "Deadly End" ]
_REPLICA_ITEM_NAME_EXCEPTIONS = [ "Replica Dragonfang's Flight" ]

def get_validator(type: QueryType) -> Callable[[dict[str], ValueRange, Sieve], bool]:
    """Returns a function that receives a `record` dictionary, `ValueRange` and a `Sieve` to determine
    whether or not the `record` is valid."""
    match type:
        case QueryType.FRAGMENT:
            return _is_fragment_valid
        case QueryType.CURRENCY:
            return _is_currency_valid
        case QueryType.ALLFLAME_EMBER:
            return _is_allflame_ember_valid
        case QueryType.GEM:
            return _is_gem_valid
        case x if x in UNIQUE_QUERY_TYPES:
            return _is_unique_valid
        case _:
            return _is_item_valid

def _is_fragment_valid(record: dict[str], range: ValueRange, _):
    return record[Field.CURRENCY_BASE_TYPE.value] not in _INVALID_FRAGMENT_BASE_TYPES \
        and _is_currency_valid(record, range, _)

def _is_currency_valid(record: dict[str], range: ValueRange, _):
    return record[Field.CURRENCY_VALUE.value] in range

def _is_unique_valid(record: dict[str], range: ValueRange, sieve: Sieve):
    unique_name: str = record[Field.NAME.value]
    is_replica = unique_name.startswith(f"{REPLICA} ") and unique_name not in _REPLICA_ITEM_NAME_EXCEPTIONS
    pattern = {
        CLASS: record[Field.CLASS.value],
        REPLICA: is_replica,
        LINKED_SOCKETS: record[Field.LINKS.value] \
            if Field.LINKS.value in record else 0 }
    return pattern in sieve and _is_item_valid(record, range, sieve)

def _is_allflame_ember_valid(record: dict[str], range: ValueRange, sieve: Sieve):
    pattern = { ITEM_LEVEL: record[Field.LEVEL_REQUIRED.value] }
    return pattern in sieve and _is_item_valid(record, range, sieve)

def _is_gem_valid(record: dict[str], range: ValueRange, sieve: Sieve):
    pattern = {
        GEM_LEVEL: record[Field.GEM_LEVEL.value],
        QUALITY: record[Field.GEM_QUALITY.value] \
            if Field.GEM_QUALITY.value in record else 0,
        CORRUPTED: record[Field.CORRUPTED.value] \
            if Field.CORRUPTED.value in record else False }
    return pattern in sieve and _is_item_valid(record, range, sieve)

def _is_item_valid(record: dict[str], range: ValueRange, _):
    return record[Field.ITEM_VALUE_FIELD.value] in range