from enum import Enum
from datetime import timedelta

class Expiration(Enum):
    """Represents an amount of time that a cache entry remains non-stale for."""
    IMMEDIATE = timedelta(seconds=0)
    DAILY = timedelta(days=1, hours=1)
    WEEKLY = timedelta(weeks=1, hours=2)
    MONTHLY = timedelta(weeks=4, hours=3)