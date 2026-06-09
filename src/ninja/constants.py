from enum import StrEnum

type Record = dict[str]
"""A record for an item obtained from `poe.ninja`."""

type RecordsJSON = dict[str]
"""The entire response with all records contained fetched from `poe.ninja`."""

class Field(StrEnum):
    """Represents the JSON fields that appear on poe.ninja reponses."""
    ID = "id"
    LINES = "lines"
    ITEMS = "items"
    LINKS = "links"
    CLASS = "itemClass"
    NAME = "name"
    GEM_QUALITY = "gemQuality"
    LEVEL_REQUIRED = "levelRequired"
    CORRUPTED = "corrupted"
    GEM_LEVEL = "gemLevel"
    PRIMARY_VALUE = "primaryValue"
    BASE_TYPE = "baseType"
    CHAOS_VALUE = "chaosValue"
    VARIANT = "variant"
    TARGET = "target" # this is an artificial field added during formatting

class BaseQueryType(StrEnum):
    """Represents the base item types that can be queried via `poe.ninja`."""
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
    RUNIC_ARTIFACT = "Artifact"
    ASTROLABE = "Astrolabe"
    DJINN_COIN = "DjinnCoin"
    WOMBGIFT = "Wombgift"
    UNIQUE_WEAPON = "UniqueWeapon"
    UNIQUE_ARMOUR = "UniqueArmour"
    UNIQUE_ACCESSORY = "UniqueAccessory"
    UNIQUE_FLASK = "UniqueFlask"
    UNIQUE_JEWEL = "UniqueJewel"
    UNIQUE_MAP = "UniqueMap"
    UNIQUE_RELIC = "UniqueRelic"
    UNIQUE_TINCTURE = "UniqueTincture"

class MiscQueryType(StrEnum):
    """Represents miscellaneous types that can be queried via `poe.ninja`."""
    CLUSTER_JEWEL = "ClusterJewel"