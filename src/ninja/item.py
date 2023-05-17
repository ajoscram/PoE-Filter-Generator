import wiki

from enum import Enum
from . import common

_URL = "https://poe.ninja/api/data/itemoverview?league={0}&type={1}"
_UNIQUE_ITEM_TYPES = [ "UniqueWeapon", "UniqueArmour", "UniqueAccessory", "UniqueFlask", "UniqueJewel", "UniqueMap" ]

_NAME_FIELD = "name"
_BASE_TYPE_FIELD = "baseType"
_VALUE_FIELD = "chaosValue"
_CLASS_FIELD = "itemType"
_LINKS_FIELD = "links"
_REPLICA_UNIQUE_PREFIX = "Replica "

class MiscItemType(Enum):
    OIL = "Oil"
    INCUBATOR = "Incubator"
    SCARAB = "Scarab"
    FOSSIL = "Fossil"
    RESONATOR = "Resonator"
    ESSENCE = "Essence"
    DIVINATION_CARD = "DivinationCard"
    BEAST = "Beast"
    INVITATION = "Invitation"
    VIAL = "Vial"
    DELIRIUM_ORB = "DeliriumOrb"

class UniqueFilter:
    classes: list[str] = None
    is_replica: bool = None
    min_links: int = None
    max_links: int = None

def get_misc_base_types(league_name: str, type: MiscItemType, lower: float, upper: float = None):
    url = _URL.format(league_name, type.value)
    return [
        record[_NAME_FIELD]
        for record in common.get_records(url)
        if common.is_value_within_range(record[_VALUE_FIELD], lower, upper)
    ]

def get_unique_base_types(league_name: str, unique_filter: UniqueFilter, lower: float, upper: float = None):
    urls = [ _URL.format(league_name, item_type) for item_type in _UNIQUE_ITEM_TYPES ]
    return list(set(
        record[_BASE_TYPE_FIELD]
        for url in urls for record in common.get_records(url)
        if common.is_value_within_range(record[_VALUE_FIELD], lower, upper) and
            _is_unique_record_valid(record, unique_filter)
    ))

def _is_unique_record_valid(record, filter: UniqueFilter):
    return \
        _is_class_valid(record, filter.classes) and \
        _is_replica_valid(record, filter.is_replica) and \
        _are_links_valid(record, filter.min_links, filter.max_links)

def _is_class_valid(record, expected_classes: list[str] = None):
    if expected_classes == None:
        return True
    
    if _CLASS_FIELD not in record:
        record[_CLASS_FIELD] = wiki.get_class_for_base_type(record[_BASE_TYPE_FIELD])
    
    if record[_CLASS_FIELD] not in expected_classes:
        return False
    
    return True

def _is_replica_valid(unique_record, should_be_replica: bool = None):
    if should_be_replica == None:
        return True
    
    is_replica = unique_record[_NAME_FIELD].startswith(_REPLICA_UNIQUE_PREFIX)
    
    if should_be_replica and not is_replica:
        return False
    
    if not should_be_replica and is_replica:
        return False
    
    return True

def _are_links_valid(record, min_links: int = None, max_links: int = None):
    if min_links == None and max_links == None:
        return True

    if _LINKS_FIELD not in record:
        record[_LINKS_FIELD] = 0

    if min_links != None and record[_LINKS_FIELD] < min_links:
        return False
    
    if max_links != None and record[_LINKS_FIELD] > max_links:
        return False
    
    return True