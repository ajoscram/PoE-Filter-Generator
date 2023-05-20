from enum import Enum
from . import common

_URL = "https://poe.ninja/api/data/currencyoverview?league={0}&type={1}"
_BASE_TYPE_FIELD = "currencyTypeName"
_VALUE_FIELD = "chaosEquivalent"
_INVALID_FRAGMENT_BASE_TYPES = [ "Will of Chaos", "Ignominious Fate", "Victorious Fate", "Deadly End" ]

class CurrencyType(Enum):
    """Represents the item types that can be queried via a `currencyoverview` link."""
    BASIC = "Currency"
    FRAGMENT = "Fragment"

def get_currency_base_types(league_name: str, type: CurrencyType, lower: float, upper: float = None):
    """Returns all base type names given a currency `type` for the `league` specified."""
    url = _URL.format(league_name, type.value)
    return [
        record[_BASE_TYPE_FIELD]
        for record in common.get_records(url)
        if common.is_value_within_range(record[_VALUE_FIELD], lower, upper) and
            record[_BASE_TYPE_FIELD] not in _INVALID_FRAGMENT_BASE_TYPES
    ]