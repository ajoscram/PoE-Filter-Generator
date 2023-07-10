import requests
from requests import ReadTimeout, ConnectTimeout, HTTPError, Timeout
from core import ExpectedError

_HEADERS = { 'User-Agent': "PoE Filter Generator https://github.com/ajoscram/PoE-Filter-Generator/" }

_ERROR_MESSAGE_PREFIX = "Error while getting {0}.\n"
_HTTP_ERROR = _ERROR_MESSAGE_PREFIX + "You might want to report this error to @ajoscram on Github with this text:\n\n{1}"
_CONNECTION_ERROR = _ERROR_MESSAGE_PREFIX + "Please make sure you have an active internet connection."

_get_cache: dict[str, dict] = {}

def http_get(url: str, resource_description_for_error: str):
    """Performs a `get` request on the `url` passed in. If successful, it returns the `json` object obtained from the request.
    If it fails, the `resource_description_for_error` is used to personalize the `ExpectedError` message raised."""
    global _get_cache
    try:
        if url not in _get_cache:
            response = requests.get(url, headers=_HEADERS)
            response.raise_for_status()
            _get_cache[url] = response.json()
        return _get_cache[url]
    except HTTPError as error:
        raise ExpectedError(_HTTP_ERROR.format(resource_description_for_error, error))
    except (ConnectTimeout, ReadTimeout, Timeout, requests.ConnectionError):
        raise ExpectedError(_CONNECTION_ERROR.format(resource_description_for_error))