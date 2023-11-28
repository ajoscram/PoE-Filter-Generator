import os, requests
from requests import ReadTimeout, ConnectTimeout, HTTPError, Timeout, ConnectionError
from core import ExpectedError
from io import BufferedWriter
from .cache_entry import Expiration
from . import cache

_HEADERS = { "User-Agent": "PoE Filter Generator https://github.com/ajoscram/PoE-Filter-Generator/" }
_DOWNLOAD_CHUNK_SIZE = 1024 * 8 # eight megabytes
_TEMP_DOWNLOAD_PREFIX = "temp_"

_HTTP_ERROR = """An HTTP error occurred while requesting data from this URL:

{0}

Error information:
    {1}"""

_CONNECTION_ERROR = """A connection error occurred while requesting data from this URL:

{0}

One of the following things is likely happening here:
- You currently don't have an active internet connection.
- The server where data is being requested from is currently down."""
_UNEXISTENT_DIRECTORY_ERROR = "'{0}' does not correspond to an existing directory on this computer."

def get(url: str, json: bool = True, expiration: Expiration = Expiration.MONTHLY, custom_http_errors: dict[int, str] = {}):
    """Performs a `get` request on the `url` passed in.
    - If successful and `json=True`, the `json` object obtained from the request is returned.
    - If successful and `json=False`, the request's body is returned as a string.
    - `expiration` determines the amount of time before deleting the object's from the cache.
    - If it fails with an HTTP error and its code is a key in the `custom_http_errors` dictionary,
    the custom error message is displayed instead."""
    data = cache.try_get(url)
    if data == None:
        response = _get_response(url, custom_http_errors)
        data = response.json() if json else response.text
        cache.add(url, expiration, json, data)
    return data

def download(url: str, directory: str, filename: str, custom_http_errors: dict[int, str] = {}):
    """Downloads a file and places it in `directory` with the `filename` passed in.
    - This operation overwrites if there's a previous file with the same name.
    - If it fails with an HTTP error and its code is a key in the `custom_http_errors` dictionary,
    the custom error message is displayed instead."""
    if not os.path.isdir(directory):
        raise ExpectedError(_UNEXISTENT_DIRECTORY_ERROR.format(directory))
    temp_filepath = os.path.join(directory, _TEMP_DOWNLOAD_PREFIX + filename)
    
    response = _get_response(url, custom_http_errors, stream=True)
    with open(temp_filepath, 'wb') as file:
        for chunk in response.iter_content(chunk_size=_DOWNLOAD_CHUNK_SIZE):
            _try_write_chunk(file, chunk)
    
    final_filepath = os.path.join(directory, filename)
    if os.path.isfile(final_filepath):
        os.remove(final_filepath)
    os.rename(temp_filepath, final_filepath)

def _get_response(url: str, custom_http_errors: dict[int, str], stream=False):
    try:
        response = requests.get(url, headers=_HEADERS, stream=stream)
        response.raise_for_status()
        return response
    except HTTPError as error:
        status_code = error.response.status_code
        if status_code in custom_http_errors:
            raise ExpectedError(custom_http_errors[status_code])
        raise ExpectedError(_HTTP_ERROR.format(url, error))
    except (ConnectTimeout, ReadTimeout, Timeout, ConnectionError):
        raise ExpectedError(_CONNECTION_ERROR.format(url))

def _try_write_chunk(file_writer: BufferedWriter, chunk):
    if not chunk:
        return
    file_writer.write(chunk)
    file_writer.flush()
    os.fsync(file_writer.fileno())