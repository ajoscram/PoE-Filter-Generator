import repoe
from typing import Callable
from core import Sieve, Operand
from .value_range import ValueRange
from .constants import Field, Record, RecordsJSON

_REPLICA_ITEM_NAME_EXCEPTIONS = [ "Replica Dragonfang's Flight" ]

type TargetGetter = Callable[[Record, RecordsJSON], str]
"""Represents any function that obtains a `Record`'s `target` item to return."""

def get_target_by_base_type(record: Record, _):
    """Gets a `record`'s `BaseType` property."""
    return record[Field.BASE_TYPE]

def get_target_by_name(record: Record, _)  :
    """Gets a `record`'s `name` property."""
    return record[Field.NAME]

def get_target_from_items(record: Record, records_json: RecordsJSON) -> str:
    """Gets a `record`'s `name` by looking up it's `id` in the `records_json`'s `items` property."""
    id = record[Field.ID]
    items = records_json[Field.ITEMS]
    item = next(i for i in items if i[Field.ID] == id)
    return item[Field.NAME]

def get_target_for_cluster(record: Record, _):
    """Gets a cluster jewel's enchant name to be used as a """
    jewel_stats: str = record[Field.NAME]
    first_stat = jewel_stats.split(",")[0]
    return repoe.get_cluster_enchant(first_stat)

type ValueGetter = Callable[[Record], float]
"""Represents any function that obtains `Record`'s value in chaos."""

def get_value_by_chaos(record: Record) -> float:
    """Gets the `record`'s value via a property with the same name."""
    return record[Field.CHAOS_VALUE]

def get_value_by_primary(record: Record) -> float:
    """Gets the `record`'s value via it's primary value."""
    return record[Field.PRIMARY_VALUE]

type Validator = Callable[[Record, ValueRange, Sieve], bool]
"""Validates that a `record` is within the `ValueRange` and meets the `Sieve`'s criteria if applicable."""

def is_item_valid(record: Record, range: ValueRange, _):
    """Checks if any `record` is valid."""
    return record[Field.CHAOS_VALUE] in range

def is_unique_valid(record: Record, range: ValueRange, sieve: Sieve):
    """Checks if a unique item's `record` is valid."""
    name: str = record[Field.NAME]
    is_foulborn = name.startswith(f"{Operand.FOULBORN} ")
    is_replica = name.startswith(f"{Operand.REPLICA} ") and name not in _REPLICA_ITEM_NAME_EXCEPTIONS
    links = record[Field.LINKS] if Field.LINKS in record else 0
    pattern = {
        Operand.CLASS: record[Field.CLASS],
        Operand.REPLICA: is_replica,
        Operand.FOULBORN: is_foulborn,
        Operand.LINKED_SOCKETS: links }
    return pattern in sieve and is_item_valid(record, range, sieve)

def is_gem_valid(record: Record, range: ValueRange, sieve: Sieve):
    """Checks if a gem's `record` is valid."""
    pattern = {
        Operand.GEM_LEVEL: record[Field.GEM_LEVEL],
        Operand.QUALITY: record[Field.GEM_QUALITY] \
            if Field.GEM_QUALITY in record else 0,
        Operand.CORRUPTED: record[Field.CORRUPTED] \
            if Field.CORRUPTED in record else False }
    return pattern in sieve and is_item_valid(record, range, sieve)

def is_cluster_jewel_valid(record: Record, range: ValueRange, sieve: Sieve):
    """Checks if a cluster jewel's `record` is valid."""
    variant: str = record[Field.VARIANT]
    pattern = {
        Operand.BASE_TYPE: record[Field.BASE_TYPE],
        Operand.ITEM_LEVEL: record[Field.LEVEL_REQUIRED],
        Operand.ENCHANTMENT_PASSIVE_NUM: int(variant.split()[0]) }
    return pattern in sieve and is_item_valid(record, range, sieve)

def is_wombgift_valid(record: Record, range: ValueRange, sieve: Sieve):
    """Checks if a wombgift's `record` is valid."""
    pattern = { Operand.ITEM_LEVEL: record[Field.LEVEL_REQUIRED] }
    return pattern in sieve and is_item_valid(record, range, sieve)