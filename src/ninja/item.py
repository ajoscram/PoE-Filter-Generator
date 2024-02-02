from . import common
from enum import Enum
from core import Sieve, REPLICA, LINKED_SOCKETS, CLASS
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

def get_misc_base_types(league_name: str, type: MiscItemType, lower: float, upper: float = None):
    """Returns a set of all base type names given a miscellaneous `type` for the `league` specified."""
    url = _URL.format(league_name, type.value)
    return {
        record[_NAME_FIELD]
        for record in common.get_records(url)
        if common.is_value_within_range(record[_VALUE_FIELD], lower, upper) }

def get_unique_base_types(league_name: str, sieve: Sieve, lower: float, upper: float = None):
    """Returns a set of all base type names for uniques filtered by `sieve` for the `league` specified."""
    urls = [ _URL.format(league_name, item_type) for item_type in _UNIQUE_ITEM_TYPES ]
    return {
        record[BASE_TYPE_FIELD]
        for url in urls for record in common.get_records(url)
        if common.is_value_within_range(record[_VALUE_FIELD], lower, upper) and
            _get_pattern_for_unique(record) in sieve }

def _get_pattern_for_unique(record: dict[str]):
    unique_name: str = record[_NAME_FIELD]
    is_replica = unique_name.startswith(_REPLICA_UNIQUE_PREFIX) and unique_name not in _REPLICA_NAME_EXCEPTIONS
    return {
        REPLICA: is_replica,
        LINKED_SOCKETS: record[LINKS_FIELD],
        CLASS: record[ITEM_CLASS_FIELD] }