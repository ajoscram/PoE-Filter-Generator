from dataclasses import dataclass

@dataclass
class ValueRange:
    """Defines an interval of numerical values."""
    lower: float
    upper: float = None

    def __contains__(self, value: float):
        """Checks if `value` exists within this range."""
        return value >= self.lower and (self.upper is None or value < self.upper)