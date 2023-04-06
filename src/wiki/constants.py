from enum import Enum

COMMA = ", "

class Order(Enum):
    ASCENDING = "ASC"
    DESCENDING = "DESC"

class Operator(Enum):
    EQUALS = "="
    GREATER = ">"
    GREATER_OR_EQUALS = ">="
    LESS = "<"
    LESS_OR_EQUALS = "<="

class Table(Enum):
    ITEMS = "items"

class Field(Enum):
    NONE = ""
    NAME = "name"
    CLASS = "class"
    RARITY = "rarity"
    DROP_LEVEL = "drop_level"
    BASE_ITEM = "base_item"

FILTER_TO_INTERNAL_CLASSES = {
    "Gloves": "Gloves",
    "Incursion Items": "IncursionItem",
    "Mana Flasks": "ManaFlask",
    "One Hand Axes": "One Hand Axe",
    "Quest Items": "QuestItem",
    "Delve Stackable Socketable Currency": "DelveStackableSocketableCurrency",
    "Memory": "MemoryLine",
    "Microtransactions": "Microtransaction",
    "Claws": "Claw",
    "Body Armours": "Body Armour",
    "Blueprints": "HeistBlueprint",
    "Contracts": "HeistContract",
    "Atlas Upgrade Items": "AtlasUpgradeItem",
    "Heist Cloaks": "HeistEquipmentUtility",
    "Rings": "Ring",
    "Maps": "Map",
    "Misc Map Items": "MiscMapItem",
    "Thrusting One Hand Swords": "Thrusting One Hand Sword",
    "Staves": "Staff",
    "Metamorph Samples": "MetamorphosisDNA",
    "Divination Cards": "DivinationCard",
    "Quivers": "Quiver",
    "Sanctified Relic": "SanctumSpecialRelic",
    "One Hand Swords": "One Hand Sword",
    "Map Fragments": "MapFragment",
    "Life Flasks": "LifeFlask",
    "Bows": "Bow",
    "Two Hand Swords": "Two Hand Sword",
    "Amulets": "Amulet",
    "Two Hand Maces": "Two Hand Mace",
    "Two Hand Axes": "Two Hand Axe",
    "Relic": "Relic",
    "Sceptres": "Sceptre",
    "Stackable Currency": "StackableCurrency",
    "Sentinel": "SentinelDrone",
    "Incubators": "IncubatorStackable",
    "Expedition Logbooks": "ExpeditionLogbook",
    "Pieces": "UniqueFragment",
    "Trinkets": "Trinket",
    "Jewels": "Jewel",
    "Hybrid Flasks": "HybridFlask",
    "One Hand Maces": "One Hand Mace",
    "Heist Brooches": "HeistEquipmentReward",
    "Active Skill Gems": "Active Skill Gem",
    "Heist Tools": "HeistEquipmentTool",
    "Daggers": "Dagger",
    "Abyss Jewels": "AbyssJewel",
    "Heist Gear": "HeistEquipmentWeapon",
    "Boots": "Boots",
    "Rune Daggers": "Rune Dagger",
    "Heist Targets": "HeistObjective",
    "Pantheon Souls": "PantheonSoul",
    "Leaguestones": "Leaguestone",
    "Labyrinth Trinkets": "LabyrinthTrinket",
    "Support Skill Gems": "Support Skill Gem",
    "Labyrinth Items": "LabyrinthItem",
    "Hideout Doodads": "HideoutDoodad",
    "Fishing Rods": "FishingRod",
    "Utility Flasks": "UtilityFlask",
    "Shields": "Shield",
    "Helmets": "Helmet",
    "Warstaves": "Warstaff",
    "Belts": "Belt"
}