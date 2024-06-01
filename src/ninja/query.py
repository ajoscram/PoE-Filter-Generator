import repoe, web
from core import Sieve
from .constants import *
from .value_range import ValueRange
from . import validation

_CURRENCY_URL = "https://poe.ninja/api/data/currencyoverview?league={0}&type={1}"
_ITEM_URL = "https://poe.ninja/api/data/itemoverview?league={0}&type={1}"
_MEMORY_SPLITTER = "Memory "
_UNKNOWN_GET_MODS_QUERY_TYPE = "Cannot obtain explicit mods for {0}."

def get_bases(
    query_type: QueryType,
    league_name: str,
    sieve: Sieve,
    value_range: ValueRange) -> set[str]:
    """Returns a set of base types for a `QueryType` and `league_name`.
    The items obtained are filtered by the `sieve` if applicable, and must fall in the `value_range` specified."""
    records = _get_records(query_type, league_name, sieve, value_range)
    match query_type:
        case QueryType.FRAGMENT | QueryType.CURRENCY:
            return { record[Field.CURRENCY_BASE_TYPE] for record in records }
        case _:
            return { record[Field.ITEM_BASE_TYPE] for record in records }

def get_mods(
    query_type: QueryType,
    league_name: str,
    sieve: Sieve,
    value_range: ValueRange) -> set[str]:
    """Returns a set of mods for a `QueryType` and `league_name`.
    The items obtained are filtered by the `sieve` if applicable, and must fall in the `value_range` specified."""
    records = _get_records(query_type, league_name, sieve, value_range)
    match query_type:
        case QueryType.MEMORY:
            return { record[Field.NAME].split(_MEMORY_SPLITTER, 1)[1] for record in records }
        case _:
            raise ValueError(_UNKNOWN_GET_MODS_QUERY_TYPE.format(query_type))

def _get_records(query_type: QueryType, league_name: str, sieve: Sieve, value_range: ValueRange):
    url = _get_url(query_type, league_name)
    validator = validation.get_validator(query_type)
    return [ record
        for record in web.get(url, web.Expiration.DAILY, formatter=_format_records)
        if validator(record, value_range, sieve) ]

def _get_url(query_type: QueryType, league_name: str):
    match query_type:
        case QueryType.FRAGMENT | QueryType.CURRENCY:
            return _CURRENCY_URL.format(league_name, query_type)
        case _:
            return _ITEM_URL.format(league_name, query_type)

def _format_records(records_info: dict[str]):
    records = records_info[Field.LINES]
    return [ _get_formatted_record(record) for record in records ]

def _get_formatted_record(record: dict[str]):
    if Field.ITEM_BASE_TYPE in record:
        base = record[Field.ITEM_BASE_TYPE]
        record[Field.CLASS] = repoe.get_class_for_base(base)
    return record