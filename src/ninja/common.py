import web, repoe

_RECORD_LINES_FIELD = "lines"
ITEM_CLASS_FIELD = "itemClass"
BASE_TYPE_FIELD = "baseType"
LINKS_FIELD = "links"

def is_value_within_range(value: float, lower: float, upper: float = None):
    """Returns `True` if `value` is greater than or equal to `lower`,
    and if either `upper` is `None` or `value` is less than `upper.`"""
    return value >= lower and (upper == None or value < upper)

def get_records(url: str):
    """Returns poe.ninja item records from the `url` passed in."""
    return web.get(url, expiration=web.Expiration.DAILY, formatter=_format_records)

def _format_records(records_info: dict[str]):
    records = records_info[_RECORD_LINES_FIELD]
    return [ _get_formatted_record(record) for record in records ]

def _get_formatted_record(record: dict[str]):
    if BASE_TYPE_FIELD in record:
        
        new_item_class = repoe.get_class_for_base(record[BASE_TYPE_FIELD])
        record[ITEM_CLASS_FIELD] = new_item_class
        
        if LINKS_FIELD not in record:
            record[LINKS_FIELD] = 0

    return record