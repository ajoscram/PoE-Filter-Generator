import web
from core import Sieve
from .constants import Field, QueryType
from .value_range import ValueRange
from .formatter import Formatter
from . import utils

_EXCHANGE_URL = "https://poe.ninja/poe1/api/economy/exchange/current/overview?league={0}&type={1}"
_STASH_URL = "https://poe.ninja/poe1/api/economy/stash/current/item/overview?league={0}&type={1}"

_DEFAULT_EXCHANGE_FORMATTER = Formatter(_EXCHANGE_URL, utils.get_base_type_from_items, utils.get_value_by_primary, utils.is_item_valid)
_DEFAULT_STASH_FORMATTER = Formatter(_STASH_URL, utils.get_base_type_by_name, utils.get_value_by_chaos, utils.is_item_valid)
_UNIQUE_FORMATTER = Formatter(_STASH_URL, utils.get_base_type, utils.get_value_by_chaos, utils.is_unique_valid)

_FORMATTERS = {
    QueryType.CURRENCY: _DEFAULT_EXCHANGE_FORMATTER,
    QueryType.FRAGMENT: _DEFAULT_EXCHANGE_FORMATTER,
    QueryType.OIL: _DEFAULT_EXCHANGE_FORMATTER,
    QueryType.SCARAB: _DEFAULT_EXCHANGE_FORMATTER,
    QueryType.FOSSIL: _DEFAULT_EXCHANGE_FORMATTER,
    QueryType.RESONATOR: _DEFAULT_EXCHANGE_FORMATTER,
    QueryType.ESSENCE: _DEFAULT_EXCHANGE_FORMATTER,
    QueryType.DIVINATION_CARD: _DEFAULT_EXCHANGE_FORMATTER,
    QueryType.DELIRIUM_ORB: _DEFAULT_EXCHANGE_FORMATTER,
    QueryType.TATTOO: _DEFAULT_EXCHANGE_FORMATTER,
    QueryType.OMEN: _DEFAULT_EXCHANGE_FORMATTER,
    QueryType.ALLFLAME_EMBER: _DEFAULT_EXCHANGE_FORMATTER,
    QueryType.RUNEGRAFT: _DEFAULT_EXCHANGE_FORMATTER,
    QueryType.ASTROLABE: _DEFAULT_EXCHANGE_FORMATTER,
    QueryType.DJINN_COIN: _DEFAULT_EXCHANGE_FORMATTER,
    QueryType.RUNIC_ARTIFACT: _DEFAULT_EXCHANGE_FORMATTER,

    QueryType.UNIQUE_WEAPON: _UNIQUE_FORMATTER,
    QueryType.UNIQUE_ARMOUR: _UNIQUE_FORMATTER,
    QueryType.UNIQUE_ACCESSORY: _UNIQUE_FORMATTER,
    QueryType.UNIQUE_FLASK: _UNIQUE_FORMATTER,
    QueryType.UNIQUE_JEWEL: _UNIQUE_FORMATTER,
    QueryType.UNIQUE_MAP: _UNIQUE_FORMATTER,
    QueryType.UNIQUE_RELIC: _UNIQUE_FORMATTER,
    QueryType.UNIQUE_TINCTURE: _UNIQUE_FORMATTER,

    QueryType.INCUBATOR: _DEFAULT_STASH_FORMATTER,
    QueryType.INVITATION: _DEFAULT_STASH_FORMATTER,
    QueryType.VIAL: _DEFAULT_STASH_FORMATTER,
    
    QueryType.GEM: Formatter(_STASH_URL, utils.get_base_type_by_name, utils.get_value_by_chaos, utils.is_gem_valid),
    QueryType.WOMBGIFT: Formatter(_STASH_URL, utils.get_base_type_by_name, utils.get_value_by_chaos, utils.is_wombgift_valid),
}

def get_bases(
    query_type: QueryType,
    league_name: str,
    sieve: Sieve,
    value_range: ValueRange) -> set[str]:
    """Returns a set of base types for a `QueryType` and `league_name`.
    The items obtained are filtered by the `sieve` if applicable, and must fall in the `value_range` specified."""
    formatter = _FORMATTERS[query_type]
    url = formatter.get_url(query_type, league_name)
    return { record[Field.BASE_TYPE]
        for record in web.get(url, web.Expiration.DAILY, formatter)
        if formatter.validate(record, value_range, sieve) }