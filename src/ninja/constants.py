from enum import StrEnum

class Field(StrEnum):
    """Represents the JSON fields that appear on poe.ninja reponnses."""
    LINES = "lines"
    LINKS = "links"
    CLASS = "itemClass"
    NAME = "name"
    GEM_QUALITY = "gemQuality"
    LEVEL_REQUIRED = "levelRequired"
    CORRUPTED = "corrupted"
    GEM_LEVEL = "gemLevel"

    # currency exclusive
    CURRENCY_BASE_TYPE = "currencyTypeName"
    CURRENCY_VALUE = "chaosEquivalent"
    
    # item exclusive
    ITEM_BASE_TYPE = "baseType"
    ITEM_VALUE_FIELD = "chaosValue"

class QueryType(StrEnum):
    """Represents the item types that can be queried via `poe.ninja`."""
    CURRENCY = "Currency"
    FRAGMENT = "Fragment"
    GEM = "SkillGem"
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
    RUNEGRAFT = "Runegraft"
    UNIQUE_WEAPON = "UniqueWeapon"
    UNIQUE_ARMOUR = "UniqueArmour"
    UNIQUE_ACCESSORY = "UniqueAccessory"
    UNIQUE_FLASK = "UniqueFlask"
    UNIQUE_JEWEL = "UniqueJewel"
    UNIQUE_MAP = "UniqueMap"
    UNIQUE_RELIC = "UniqueRelic"

UNIQUE_QUERY_TYPES = {
    QueryType.UNIQUE_ACCESSORY, QueryType.UNIQUE_ARMOUR, \
    QueryType.UNIQUE_JEWEL, QueryType.UNIQUE_FLASK, \
    QueryType.UNIQUE_MAP, QueryType.UNIQUE_WEAPON, \
    QueryType.UNIQUE_RELIC }