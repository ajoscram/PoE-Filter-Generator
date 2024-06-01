from enum import StrEnum

# Operands
class Operand(StrEnum):
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

# Operators
class Operator(StrEnum):
    GREATER_EQUALS = ">="
    GREATER = ">"
    LESS_EQUALS = "<="
    LESS = "<"
    CONTAINS = "="
    EQUALS = "=="
    NOT_CONTAINS = "!"
    NOT_EQUALS = "!="

# Rules
COMMENT_START = '#'
RULE_SEPARATOR = '.'
RULE_START = COMMENT_START + RULE_SEPARATOR

# PFG
ERROR_EXIT_CODE = 1
COMMAND_START = ":"
DEFAULT_WIKI_PAGE_NAME = "Usage"
HANDLER_START = RULE_SEPARATOR
FILE_ENCODING = "utf-8"