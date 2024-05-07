import repoe, web
from core import Sieve
from .constants import *
from . import validation

class _QueryInfo:
    def __init__(self, url: str, base_type_field: str, value_field: str):
        self.url = url
        self.base_type_field = base_type_field
        self.value_field = value_field

def get_bases(
    query_type: QueryType,
    league_name: str,
    sieve: Sieve,
    lower: float,
    upper: float = None) -> set[str]:
    """Returns a set containing all base types given a `QueryType` and `league_name`.
    The items obtained are filtered by the `sieve` if applicable, and must fall in the range between `lower` and `upper`.
    If `upper` is not provided, then it is ignored and only `lower` is checked instead."""
    query_info = _get_query_info(query_type, league_name)
    validator = validation.get_validator(query_type)
    return {
        record[query_info.base_type_field]
        for record in web.get(query_info.url, expiration=web.Expiration.DAILY, formatter=_format_records)
        if _is_value_within_range(record[query_info.value_field], lower, upper) and validator(record, sieve) }

def _get_query_info(query_type: QueryType, league_name: str):
    match query_type:
        case QueryType.FRAGMENT | QueryType.CURRENCY:
            return _QueryInfo(
                CURRENCY_URL.format(league_name, query_type.value),
                CURRENCY_BASE_TYPE_FIELD,
                CURRENCY_VALUE_FIELD)
        case _:
            return _QueryInfo(
                ITEM_URL.format(league_name, query_type.value),
                ITEM_BASE_TYPE_FIELD,
                ITEM_VALUE_FIELD)

def _is_value_within_range(value: float, lower: float, upper: float = None):
    return value >= lower and (upper == None or value < upper)

def _format_records(records_info: dict[str]):
    records = records_info[RECORD_LINES_FIELD]
    return [ _get_formatted_record(record) for record in records ]

def _get_formatted_record(record: dict[str]):
    if BASE_TYPE_FIELD in record:
        
        new_item_class = repoe.get_class_for_base(record[BASE_TYPE_FIELD])
        record[ITEM_CLASS_FIELD] = new_item_class
        
        if LINKS_FIELD not in record:
            record[LINKS_FIELD] = 0

    return record