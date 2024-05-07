from core import Sieve, REPLICA, LINKED_SOCKETS, CLASS
from typing import Callable
from .constants import *

_INVALID_FRAGMENT_BASE_TYPES = [ "Will of Chaos", "Ignominious Fate", "Victorious Fate", "Deadly End" ]
_REPLICA_ITEM_NAME_EXCEPTIONS = [ "Replica Dragonfang's Flight" ]

def get_validator(type: QueryType) -> Callable[[dict[str], Sieve], bool]:
    if type == QueryType.FRAGMENT:
        return _is_fragment_record_valid
    
    if type in UNIQUE_QUERY_TYPES:
        return _is_unique_record_valid
    
    return lambda _, __: True

def _is_fragment_record_valid(record: dict[str], _):
    """Returns whether or not a fragment record is valid."""
    return record[CURRENCY_BASE_TYPE_FIELD] not in _INVALID_FRAGMENT_BASE_TYPES

def _is_unique_record_valid(record: dict[str], sieve: Sieve):
    """Returns whether or not a unique record is valid."""
    unique_name: str = record[ITEM_NAME_FIELD]
    is_replica = unique_name.startswith(f"{REPLICA} ") and unique_name not in _REPLICA_ITEM_NAME_EXCEPTIONS
    pattern = {
        REPLICA: is_replica,
        LINKED_SOCKETS: record[LINKS_FIELD],
        CLASS: record[ITEM_CLASS_FIELD] }
    return pattern in sieve