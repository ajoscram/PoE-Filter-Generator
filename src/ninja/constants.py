from enum import Enum

RECORD_LINES_FIELD = "lines"
ITEM_CLASS_FIELD = "itemClass"
LINKS_FIELD = "links"

CURRENCY_URL = "https://poe.ninja/api/data/currencyoverview?league={0}&type={1}"
CURRENCY_BASE_TYPE_FIELD = "currencyTypeName"
CURRENCY_VALUE_FIELD = "chaosEquivalent"

ITEM_URL = "https://poe.ninja/api/data/itemoverview?league={0}&type={1}"
ITEM_BASE_TYPE_FIELD = "baseType"
ITEM_VALUE_FIELD = "chaosValue"
ITEM_NAME_FIELD = "name"
ITEM_LEVEL_REQUIRED_FIELD = "levelRequired"

class QueryType(Enum):
    """Represents the item types that can be queried via `poe.ninja`."""
    CURRENCY = "Currency"
    FRAGMENT = "Fragment"
    MEMORY = "Memory"
    OIL = "Oil"
    INCUBATOR = "Incubator"
    SCARAB = "Scarab"
    FOSSIL = "Fossil"
    RESONATOR = "Resonator"
    ESSENCE = "Essence"
    DIVINATION_CARD = "DivinationCard"
    INVITATION = "Invitation"
    VIAL = "Vial"
    DELIRIUM_ORB = "DeliriumOrb"
    TATTOO = "Tattoo"
    OMEN = "Omen"
    ALLFLAME_EMBER = "AllflameEmber"
    UNIQUE_WEAPON = "UniqueWeapon"
    UNIQUE_ARMOUR = "UniqueArmour"
    UNIQUE_ACCESSORY = "UniqueAccessory"
    UNIQUE_FLASK = "UniqueFlask"
    UNIQUE_JEWEL = "UniqueJewel"
    UNIQUE_MAP = "UniqueMap"

UNIQUE_QUERY_TYPES = {
    QueryType.UNIQUE_ACCESSORY, QueryType.UNIQUE_ARMOUR, \
    QueryType.UNIQUE_FLASK, QueryType.UNIQUE_JEWEL, \
    QueryType.UNIQUE_FLASK, QueryType.UNIQUE_MAP, QueryType.UNIQUE_WEAPON }