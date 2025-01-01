from enum import StrEnum

class Delimiter(StrEnum):
    """Represents various delimiter tokens that can be found on filters."""
    COMMENT_START = "#"
    COMMAND_START = ":"
    RULE_SEPARATOR = "."
    HANDLER_START = RULE_SEPARATOR
    RULE_START = COMMENT_START + RULE_SEPARATOR
    LIST_ENTRY_SEPARATOR = ","
    PAIR_SEPARATOR = "="

class Operator(StrEnum):
    """Represents operators used to create conditions in filters."""
    GREATER_EQUALS = ">="
    GREATER = ">"
    LESS_EQUALS = "<="
    LESS = "<"
    CONTAINS = "="
    EQUALS = "=="
    NOT_CONTAINS = "!"
    NOT_EQUALS = "!="

class Operand(StrEnum):
    """Represents operands that can be used to start lines in filters."""
    HIDE = "Hide"
    SHOW = "Show"
    MINIMAL = "Minimal"
    CLASS = "Class"
    BASE_TYPE = "BaseType"
    LINKED_SOCKETS = "LinkedSockets"
    REPLICA = "Replica"
    DROP_LEVEL = "DropLevel"
    ITEM_LEVEL = "ItemLevel"
    AREA_LEVEL = "AreaLevel"
    CORRUPTED = "Corrupted"
    QUALITY = "Quality"
    GEM_LEVEL = "GemLevel"
    HAS_EXPLICIT_MOD = "HasExplicitMod"

BLOCK_STARTERS = [ Operand.HIDE, Operand.SHOW, Operand.MINIMAL ]

# Miscellaneous
ERROR_EXIT_CODE = 1
FILE_ENCODING = "utf-8"
DEFAULT_WIKI_PAGE_NAME = "Usage"
