import os
import requests
from enum import Enum
from requests import ReadTimeout, ConnectTimeout, HTTPError, Timeout, ConnectionError
from core import ExpectedError

_HEADERS = { 'User-Agent': "PoE Filter Generator https://github.com/ajoscram/PoE-Filter-Generator/" }

_HTTP_ERROR = """An HTTP error occurred while requesting data from this URL:

{0}

Error information:
    {1}"""
_CONNECTION_ERROR = """A connection error occurred while requesting data from this URL:

{0}

One of the following things is likely happening here:
- You currently don't have an active internet connection.
- The server where data is being requested from is currently down."""

_get_cache: dict[str, dict | str] = {}

def get(url: str, json: bool = True, custom_http_errors: dict[int, str] = {}):
    """Performs a `get` request on the `url` passed in.
    - If successful and `json=True`, the `json` object obtained from the request is returned.
    - If successful and `json=False`, the request's body is returned as a string.
    - If it fails with an HTTP error and its code is a key in the `custom_http_errors` dictionary,
    the custom error message is displayed instead."""
    global _get_cache
    try:
        if url not in _get_cache:
            response = requests.get(url, headers=_HEADERS)
            response.raise_for_status()
            _get_cache[url] = response.json() if json else response.text
        return _get_cache[url]
    except HTTPError as error:
        status_code = error.response.status_code
        if status_code in custom_http_errors:
            raise ExpectedError(custom_http_errors[status_code])
        raise ExpectedError(_HTTP_ERROR.format(url, error))
    except (ConnectTimeout, ReadTimeout, Timeout, ConnectionError):
        raise ExpectedError(_CONNECTION_ERROR.format(url))

def download(url: str, filename: str, directory: str = os.getcwd()):
    pass