import re
from enum import Enum

class Matchable:
    """Wraps a string to match with regular expressions on a `match` control structure or with `==`.
    The comparison made is case insensitive."""
    
    def __init__(self, string: str) -> None:
        self.string = string
        self.match: re.Match = None

    def __ne__(self, value: str | Enum) -> bool:
        return not self.__eq__(value)

    def __eq__(self, other: str | Enum):
        """Returns `True` if `other` is a matching regular expression string or `Enum` containing one.
        `False` otherwise."""
        if isinstance(other, Enum):
            other = other.value
        self.match = re.match(other, self.string, re.IGNORECASE)
        return self.match is not None

    def __getitem__(self, group_index: int):
        """Gets a group by index from the last match found."""
        return self.match[group_index]