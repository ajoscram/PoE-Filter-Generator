from enum import Enum

COMMA = ", "

class Order(Enum):
    """Represents the order to sort the results to Wiki queries."""
    ASCENDING = "ASC"
    DESCENDING = "DESC"

class Operator(Enum):
    """Represents operators used to compare fields when making queries to the Wiki."""
    EQUALS = "="
    GREATER = ">"
    GREATER_OR_EQUALS = ">="
    LESS = "<"
    LESS_OR_EQUALS = "<="

class Table(Enum):
    """Represents different table names within the Wiki."""
    ITEMS = "items"

class Field(Enum):
    """Represents the names of fields within tables in the Wiki."""
    NONE = ""
    NAME = "name"
    CLASS_ID = "class_id"
    RARITY = "rarity"
    DROP_LEVEL = "drop_level"
    BASE_ITEM = "base_item"