from core import Sieve, REPLICA, LINKED_SOCKETS, CLASS, ITEM_LEVEL
from typing import Callable
from .constants import *

_INVALID_FRAGMENT_BASE_TYPES = [ "Will of Chaos", "Ignominious Fate", "Victorious Fate", "Deadly End" ]
_REPLICA_ITEM_NAME_EXCEPTIONS = [ "Replica Dragonfang's Flight" ]

def get_validator(type: QueryType) -> Callable[[dict[str], Sieve], bool]:
    """Returns a function that receives a record dictionary and a `Sieve` to determine
    whether or not the record is valid."""
    if type == QueryType.FRAGMENT:
        return _is_fragment_record_valid
    
    if type == QueryType.ALLFLAME_EMBER:
        return _is_allflame_ember_valid
    
    if type in UNIQUE_QUERY_TYPES:
        return _is_unique_record_valid
    
    return lambda _, __: True

def _is_fragment_record_valid(record: dict[str], _):
    return record[CURRENCY_BASE_TYPE_FIELD] not in _INVALID_FRAGMENT_BASE_TYPES

def _is_unique_record_valid(record: dict[str], sieve: Sieve):
    unique_name: str = record[ITEM_NAME_FIELD]
    is_replica = unique_name.startswith(f"{REPLICA} ") and unique_name not in _REPLICA_ITEM_NAME_EXCEPTIONS
    pattern = {
        REPLICA: is_replica,
        LINKED_SOCKETS: record[LINKS_FIELD],
        CLASS: record[ITEM_CLASS_FIELD] }
    return pattern in sieve

def _is_allflame_ember_valid(record: dict[str], sieve: Sieve):
    return { ITEM_LEVEL: record[ITEM_LEVEL_REQUIRED_FIELD] } in sieve