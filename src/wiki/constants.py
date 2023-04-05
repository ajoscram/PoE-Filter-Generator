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

CLASS_FILTER_TO_ID = {
    # https://www.poewiki.net/wiki/Item_class use this here
    "Daggers": "Dagger",
    "Claws":"Claw",
}