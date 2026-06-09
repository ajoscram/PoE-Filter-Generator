import web
from core import Sieve
from .constants import Field, BaseQueryType, MiscQueryType
from .value_range import ValueRange
from .formatter import Formatter
from . import utils

_EXCHANGE_URL = "https://poe.ninja/poe1/api/economy/exchange/current/overview?league={0}&type={1}"
_STASH_URL = "https://poe.ninja/poe1/api/economy/stash/current/item/overview?league={0}&type={1}"

_DEFAULT_EXCHANGE_FORMATTER = Formatter(_EXCHANGE_URL, utils.get_target_from_items, utils.get_value_by_primary, utils.is_item_valid)
_DEFAULT_STASH_FORMATTER = Formatter(_STASH_URL, utils.get_target_by_name, utils.get_value_by_chaos, utils.is_item_valid)
_UNIQUE_FORMATTER = Formatter(_STASH_URL, utils.get_target_by_base_type, utils.get_value_by_chaos, utils.is_unique_valid)
_BASE_QUERY_FORMATTERS = {
    BaseQueryType.CURRENCY: _DEFAULT_EXCHANGE_FORMATTER,
    BaseQueryType.FRAGMENT: _DEFAULT_EXCHANGE_FORMATTER,
    BaseQueryType.OIL: _DEFAULT_EXCHANGE_FORMATTER,
    BaseQueryType.SCARAB: _DEFAULT_EXCHANGE_FORMATTER,
    BaseQueryType.FOSSIL: _DEFAULT_EXCHANGE_FORMATTER,
    BaseQueryType.RESONATOR: _DEFAULT_EXCHANGE_FORMATTER,
    BaseQueryType.ESSENCE: _DEFAULT_EXCHANGE_FORMATTER,
    BaseQueryType.DIVINATION_CARD: _DEFAULT_EXCHANGE_FORMATTER,
    BaseQueryType.DELIRIUM_ORB: _DEFAULT_EXCHANGE_FORMATTER,
    BaseQueryType.TATTOO: _DEFAULT_EXCHANGE_FORMATTER,
    BaseQueryType.OMEN: _DEFAULT_EXCHANGE_FORMATTER,
    BaseQueryType.ALLFLAME_EMBER: _DEFAULT_EXCHANGE_FORMATTER,
    BaseQueryType.RUNEGRAFT: _DEFAULT_EXCHANGE_FORMATTER,
    BaseQueryType.ASTROLABE: _DEFAULT_EXCHANGE_FORMATTER,
    BaseQueryType.DJINN_COIN: _DEFAULT_EXCHANGE_FORMATTER,
    BaseQueryType.RUNIC_ARTIFACT: _DEFAULT_EXCHANGE_FORMATTER,

    BaseQueryType.UNIQUE_WEAPON: _UNIQUE_FORMATTER,
    BaseQueryType.UNIQUE_ARMOUR: _UNIQUE_FORMATTER,
    BaseQueryType.UNIQUE_ACCESSORY: _UNIQUE_FORMATTER,
    BaseQueryType.UNIQUE_FLASK: _UNIQUE_FORMATTER,
    BaseQueryType.UNIQUE_JEWEL: _UNIQUE_FORMATTER,
    BaseQueryType.UNIQUE_MAP: _UNIQUE_FORMATTER,
    BaseQueryType.UNIQUE_RELIC: _UNIQUE_FORMATTER,
    BaseQueryType.UNIQUE_TINCTURE: _UNIQUE_FORMATTER,

    BaseQueryType.INCUBATOR: _DEFAULT_STASH_FORMATTER,
    BaseQueryType.INVITATION: _DEFAULT_STASH_FORMATTER,
    BaseQueryType.VIAL: _DEFAULT_STASH_FORMATTER,
    
    BaseQueryType.GEM: Formatter(_STASH_URL, utils.get_target_by_name, utils.get_value_by_chaos, utils.is_gem_valid),
    BaseQueryType.WOMBGIFT: Formatter(_STASH_URL, utils.get_target_by_name, utils.get_value_by_chaos, utils.is_wombgift_valid),
}

def get_base_types(query_type: BaseQueryType, league_name: str, sieve: Sieve, value_range: ValueRange) -> set[str]:
    """Returns a set of base types for a `QueryType` and `league_name`.
    The items obtained are filtered by the `sieve` if applicable, and must fall in the `value_range` specified."""
    formatter = _BASE_QUERY_FORMATTERS[query_type]
    url = formatter.get_url(query_type, league_name)
    return _get_records(url, sieve, value_range, formatter)

def get_cluster_enchants(league_name: str, sieve: Sieve, value_range: ValueRange) -> set[str]:
    formatter = Formatter(
        _STASH_URL,
        utils.get_target_for_cluster,
        utils.get_value_by_chaos,
        utils.is_cluster_jewel_valid)
    url = formatter.get_url(MiscQueryType.CLUSTER_JEWEL, league_name)
    return _get_records(url, sieve, value_range, formatter)

def _get_records(url: str, sieve: Sieve, value_range: ValueRange, formatter: Formatter):
    return { record[Field.TARGET]
        for record in web.get(url, web.Expiration.DAILY, formatter)
        if formatter.validate(record, value_range, sieve) }