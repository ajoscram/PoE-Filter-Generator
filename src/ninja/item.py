from enum import Enum
from . import common
from core import REPLICA
from .common import BASE_TYPE_FIELD, ITEM_CLASS_FIELD, LINKS_FIELD

_URL = "https://poe.ninja/api/data/itemoverview?league={0}&type={1}"
_UNIQUE_ITEM_TYPES = [ "UniqueWeapon", "UniqueArmour", "UniqueAccessory", "UniqueFlask", "UniqueJewel", "UniqueMap" ]

_NAME_FIELD = "name"
_VALUE_FIELD = "chaosValue"
_REPLICA_UNIQUE_PREFIX = f"{REPLICA} "
_REPLICA_NAME_EXCEPTIONS = [ "Replica Dragonfang's Flight" ]

class MiscItemType(Enum):
    """Represents the miscellaneous item types that can be obtained via an `itemoverview` link."""
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
    TATTOO = "Tattoo"
    OMEN = "Omen"

class UniqueFilter:
    classes: list[str] = None
    is_replica: bool = None
    links_range: (int, int) = (0, 6)

def get_misc_base_types(league_name: str, type: MiscItemType, lower: float, upper: float = None):
    """Returns all base type names given a miscellaneous `type` for the `league` specified."""
    url = _URL.format(league_name, type.value)
    return [
        record[_NAME_FIELD]
        for record in common.get_records(url)
        if common.is_value_within_range(record[_VALUE_FIELD], lower, upper) ]

def get_unique_base_types(league_name: str, unique_filter: UniqueFilter, lower: float, upper: float = None):
    """Returns all base type names for uniques filtered by a `unique_filter` for the `league` specified."""
    urls = [ _URL.format(league_name, item_type) for item_type in _UNIQUE_ITEM_TYPES ]

    return list(set(
        record[BASE_TYPE_FIELD]
        for url in urls for record in common.get_records(url)
        if common.is_value_within_range(record[_VALUE_FIELD], lower, upper) and
            _is_unique_record_valid(record, unique_filter)))

def _is_unique_record_valid(record: dict[str], filter: UniqueFilter):
    return \
        _is_class_valid(record, filter.classes) and \
        _is_replica_valid(record, filter.is_replica) and \
        _are_links_valid(record, filter.links_range)

def _is_class_valid(record: dict[str], expected_classes: list[str] = None):
    if expected_classes == None:
        return True

    return record[ITEM_CLASS_FIELD] in expected_classes

def _is_replica_valid(unique_record: dict[str], should_be_replica: bool = None):
    if should_be_replica == None:
        return True
    
    unique_name: str = unique_record[_NAME_FIELD]
    is_replica = unique_name.startswith(_REPLICA_UNIQUE_PREFIX) and unique_name not in _REPLICA_NAME_EXCEPTIONS
    return should_be_replica == is_replica

def _are_links_valid(record: dict[str], links: (int, int)):
    min_links = links[0]
    max_links = links[1]
    return record[LINKS_FIELD] >= min_links and record[LINKS_FIELD] <= max_links