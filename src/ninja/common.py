import web

_RESPONSE_DATA_LOCATION = "lines"

def is_value_within_range(value: float, lower: float, upper: float = None):
    """Returns `True` if `value` is greater than or equal to `lower`,
    and if either `upper` is `None` or `value` is less than `upper.`"""
    return value >= lower and (upper == None or value < upper)

def get_records(url: str):
    """Returns poe.ninja item records from the `url` passed in."""
    response = web.get(url)
    return response[_RESPONSE_DATA_LOCATION]