import pytest, utils, requests
from test_utilities import FunctionMock
from pytest import MonkeyPatch
from requests import ConnectTimeout, HTTPError, ReadTimeout, Timeout
from utils.http import _HEADERS, _HTTP_ERROR, _CONNECTION_ERROR
from core import ExpectedError

class _MockHttpResponse:
    def __init__(self): self.json_response = {}
    def raise_for_status(self): pass
    def json(self): return self.json_response

_HTTP_RESOURCE_DESCRIPTION = "http resource description"
_URL = "url"

@pytest.fixture(autouse=True)
def setup():
    utils.http._get_cache = {}

def test_http_get_given_a_url_should_get_the_json(monkeypatch: MonkeyPatch):
    MOCK_RESPONSE = _MockHttpResponse()
    get_mock = FunctionMock(monkeypatch, requests.get, MOCK_RESPONSE)

    response = utils.http_get(_URL, None)

    assert get_mock.received(_URL, headers=_HEADERS)
    assert response == MOCK_RESPONSE.json_response

def test_http_get_given_multiple_requests_on_the_same_url_should_return_the_cached_value(monkeypatch: MonkeyPatch):
    MOCK_RESPONSE = _MockHttpResponse()
    get_mock = FunctionMock(monkeypatch, requests.get, MOCK_RESPONSE)
    
    _ = utils.http_get(_URL, None)
    _ = utils.http_get(_URL, None)

    assert get_mock.get_invocation_count() == 1 # when the cache is hit only one request is expected

def test_http_get_given_an_http_error_should_raise(monkeypatch: MonkeyPatch):
    HTTP_ERROR = HTTPError()
    _ = FunctionMock(monkeypatch, requests.get, HTTP_ERROR)
    
    with pytest.raises(ExpectedError) as error:
        _ = utils.http_get(_URL, _HTTP_RESOURCE_DESCRIPTION)

    assert error.value.message == _HTTP_ERROR.format(_HTTP_RESOURCE_DESCRIPTION, HTTP_ERROR)

@pytest.mark.parametrize("error_to_raise", [ ConnectTimeout, ReadTimeout, Timeout, requests.ConnectionError ])
def test_http_get_given_a_connection_error_should_raise(monkeypatch: MonkeyPatch, error_to_raise: Exception):
    _ = FunctionMock(monkeypatch, requests.get, error_to_raise)
    
    with pytest.raises(ExpectedError) as error:
        _ = utils.http_get(_URL, _HTTP_RESOURCE_DESCRIPTION)

    assert error.value.message == _CONNECTION_ERROR.format(_HTTP_RESOURCE_DESCRIPTION)