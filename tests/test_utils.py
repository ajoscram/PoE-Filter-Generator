import pytest, utils, requests
from test_utilities import FunctionMock
from pytest import MonkeyPatch
from requests import ConnectTimeout, HTTPError, ReadTimeout, Timeout
from utils.http import _HEADERS, _HTTP_ERROR, _CONNECTION_ERROR
from core import GeneratorError

class _MockHttpResponse:
    def __init__(self): self.json_response = {}
    def raise_for_status(self): pass
    def json(self): return self.json_response

_HTTP_RESOURCE_DESCRIPTION = "http resource description"

@pytest.fixture
def url():
    # resetting the cache in utils.http is necessary here because it is a global varible.
    utils.http._get_cache = {}
    return "url"

def test_http_get_given_a_url_should_get_the_json(monkeypatch: MonkeyPatch, url: str):
    MOCK_RESPONSE = _MockHttpResponse()
    get_mock = FunctionMock(monkeypatch, requests.get, MOCK_RESPONSE)

    response = utils.http_get(url, None)

    assert get_mock.received(url, headers=_HEADERS)
    assert response == MOCK_RESPONSE.json_response

def test_http_get_given_multiple_requests_on_the_same_url_should_return_the_cached_value(
    monkeypatch: MonkeyPatch, url: str):
    MOCK_RESPONSE = _MockHttpResponse()
    get_mock = FunctionMock(monkeypatch, requests.get, MOCK_RESPONSE)
    
    _ = utils.http_get(url, None)
    _ = utils.http_get(url, None)

    assert get_mock.get_invocation_count() == 1 # when the cache is hit only one request is expected

def test_http_get_given_an_http_error_should_raise(monkeypatch: MonkeyPatch, url: str):
    HTTP_ERROR = HTTPError()
    _ = FunctionMock(monkeypatch, requests.get, HTTP_ERROR)
    
    with pytest.raises(GeneratorError) as error:
        _ = utils.http_get(url, _HTTP_RESOURCE_DESCRIPTION)

    assert error.value.message == _HTTP_ERROR.format(_HTTP_RESOURCE_DESCRIPTION, HTTP_ERROR)

@pytest.mark.parametrize("error_to_raise", [ ConnectTimeout, ReadTimeout, Timeout, requests.ConnectionError ])
def test_http_get_given_a_connection_error_should_raise(
    monkeypatch: MonkeyPatch, url: str, error_to_raise: Exception):
    _ = FunctionMock(monkeypatch, requests.get, error_to_raise)
    
    with pytest.raises(GeneratorError) as error:
        _ = utils.http_get(url, _HTTP_RESOURCE_DESCRIPTION)

    assert error.value.message == _CONNECTION_ERROR.format(_HTTP_RESOURCE_DESCRIPTION)