import utils

_NINJA_DATA_DESCRIPTOR = "data from poe.ninja"
_RESPONSE_DATA_LOCATION = "lines"

def is_value_within_range(value: float, lower: float, upper: float = None):
    return value >= lower and (upper == None or value < upper)

def get_records(url: str):
    response = utils.http_get(url, _NINJA_DATA_DESCRIPTOR)
    return response[_RESPONSE_DATA_LOCATION]