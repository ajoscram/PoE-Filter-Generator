import pytest, web, requests, os
from test_utilities import FunctionMock, OpenMock
from pytest import MonkeyPatch
from requests import ConnectTimeout, HTTPError, ReadTimeout, Timeout, ConnectionError
from web.functions import _JSON_CONTENT_TYPE, _CONTENT_TYPE_HEADER, _HEADERS, _HTTP_ERROR as _HTTP_ERROR_TEXT, _CONNECTION_ERROR, _TEMP_DOWNLOAD_PREFIX, _UNEXISTENT_DIRECTORY_ERROR
from core import ExpectedError
from web import cache

class _MockHttpResponse:
    def __init__(self, content_type: str = _JSON_CONTENT_TYPE):
        self.json_response = { "some": "json" }
        self.text = str(self.json_response)
        self.status_code = 1
        self.content = [ "1", "2", None, "3" ] # None here emulates faulty chunks of data
        self.headers = { _CONTENT_TYPE_HEADER: content_type }
    
    def raise_for_status(self):
        pass
    
    def iter_content(self, chunk_size: int):
        return self.content

    def json(self):
        return self.json_response

_MOCK_RESPONSE = _MockHttpResponse()
_HTTP_ERROR = HTTPError(response=_MOCK_RESPONSE)
_URL = "url"
_DIRECTORY = "directory"
_FILENAME = "file.name"
_CUSTOM_ERROR_MESSAGE = "custom error message"

@pytest.fixture(autouse=True)
def request_get_mock(monkeypatch: MonkeyPatch):
    return FunctionMock(monkeypatch, requests.get, _MOCK_RESPONSE)

@pytest.fixture(autouse=True)
def cache_try_get_mock(monkeypatch: MonkeyPatch):
    return FunctionMock(monkeypatch, cache.try_get, target=cache)

@pytest.fixture(autouse=True)
def cache_add_mock(monkeypatch: MonkeyPatch):
    return FunctionMock(monkeypatch, cache.add, target=cache)

def test_get_given_a_url_and_headers_should_get_the_json(request_get_mock: FunctionMock):
    response = web.get(_URL)

    assert request_get_mock.received(_URL, headers=_HEADERS)
    assert response == _MOCK_RESPONSE.json_response

def test_get_given_text_content_type_should_return_the_text_instead(request_get_mock: FunctionMock):
    text_response = _MockHttpResponse("application/text")
    request_get_mock.result = text_response
    
    response = web.get(_URL)

    assert response == text_response.text

def test_get_given_value_is_cached_should_return_the_cached_value(
    cache_try_get_mock: FunctionMock, request_get_mock: FunctionMock):
    
    cache_try_get_mock.result = _MOCK_RESPONSE

    response = web.get(_URL)

    assert response == _MOCK_RESPONSE
    assert request_get_mock.get_invocation_count() == 0

def test_get_given_a_formatter_should_apply_it_before_adding_it_to_cache_and_return_the_formatted_data(
    cache_add_mock: FunctionMock):

    FORMATTED_DATA = "formatted data"
    formatter = lambda _: FORMATTED_DATA

    response = web.get(_URL, formatter=formatter)

    assert response == FORMATTED_DATA
    assert cache_add_mock.received(FORMATTED_DATA)

def test_get_given_an_http_error_should_raise(request_get_mock: FunctionMock):
    request_get_mock.result = _HTTP_ERROR
    
    with pytest.raises(ExpectedError) as error:
        _ = web.get(_URL)

    assert error.value.message == _HTTP_ERROR_TEXT.format(_URL, _HTTP_ERROR)

def test_get_given_a_custom_http_error_should_raise_with_it_instead(request_get_mock: FunctionMock):
    request_get_mock.result = _HTTP_ERROR

    with pytest.raises(ExpectedError) as error:
        _ = web.get(_URL, custom_http_errors={ _MOCK_RESPONSE.status_code: _CUSTOM_ERROR_MESSAGE })

    assert error.value.message == _CUSTOM_ERROR_MESSAGE

@pytest.mark.parametrize("error_to_raise", [ ConnectTimeout, ReadTimeout, Timeout, ConnectionError ])
def test_get_given_a_connection_error_should_raise(request_get_mock: FunctionMock, error_to_raise: Exception):
    request_get_mock.result = error_to_raise
    
    with pytest.raises(ExpectedError) as error:
        _ = web.get(_URL)

    assert error.value.message == _CONNECTION_ERROR.format(_URL)

def test_download_should_download_the_resource_in_the_url_and_replace_the_previous_file(
    monkeypatch: MonkeyPatch, request_get_mock: FunctionMock):
    
    FILEPATH = "filepath"
    os_path_isdir_mock = FunctionMock(monkeypatch, os.path.isdir, True)
    os_path_isfile_mock = FunctionMock(monkeypatch, os.path.isfile, True)
    os_path_join_mock = FunctionMock(monkeypatch, os.path.join, FILEPATH)
    os_remove_mock = FunctionMock(monkeypatch, os.remove)
    os_rename_mock = FunctionMock(monkeypatch, os.rename)
    open_mock = OpenMock(monkeypatch)

    web.download(_URL, _DIRECTORY, _FILENAME)

    assert os_path_isdir_mock.received(_DIRECTORY)
    assert os_path_join_mock.received(_DIRECTORY, _TEMP_DOWNLOAD_PREFIX + _FILENAME)
    assert request_get_mock.received(_URL, stream=True)
    assert open_mock.received(FILEPATH, 'wb')
    for value in filter(lambda x: x != None, _MOCK_RESPONSE.content):
        assert open_mock.file.got_written(value)
    assert os_path_join_mock.received(_DIRECTORY, _FILENAME)
    assert os_path_isfile_mock.received(FILEPATH)
    assert os_remove_mock.received(FILEPATH)
    assert os_rename_mock.received(FILEPATH, FILEPATH)

def test_download_given_directory_does_not_exist_should_raise(monkeypatch: MonkeyPatch):
    _ = FunctionMock(monkeypatch, os.path.isdir, False)

    with pytest.raises(ExpectedError) as error:
        web.download(_URL, _DIRECTORY, _FILENAME)
    
    assert error.value.message == _UNEXISTENT_DIRECTORY_ERROR.format(_DIRECTORY)

def test_download_given_a_custom_http_error_should_raise_with_it_instead(
    monkeypatch: MonkeyPatch, request_get_mock: FunctionMock):
    
    request_get_mock.result = _HTTP_ERROR
    _ = FunctionMock(monkeypatch, os.path.isdir, True)

    with pytest.raises(ExpectedError) as error:
        web.download(_URL, _DIRECTORY, _FILENAME, custom_http_errors={ _MOCK_RESPONSE.status_code: _CUSTOM_ERROR_MESSAGE })

    assert error.value.message == _CUSTOM_ERROR_MESSAGE