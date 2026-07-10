from enum import StrEnum

class RuleName(StrEnum):
    IMPORT = "import"
    NAME = "name"

class Navigation(StrEnum):
    IN = ">"
    OUT = "<"

class Splitter(StrEnum):
    ROOT = "|"
    BLOCKNAME = "->"
    TEMPLATE = "{"