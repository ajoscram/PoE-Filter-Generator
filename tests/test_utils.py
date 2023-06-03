import pytest, utils, requests
from pytest import MonkeyPatch
from requests import ConnectTimeout, HTTPError, ReadTimeout, Timeout
from utils.http import _HEADERS, _HTTP_ERROR, _CONNECTION_ERROR
from core import GeneratorError

class MockHttpResponse:
    def __init__(self): self.json_response = {}
    def raise_for_status(self): pass
    def json(self): return self.json_response

@pytest.fixture
def url():
    # resetting the cache in utils.http is necessary here because it is a global varible.
    utils.http._get_cache = {}
    return "url"

HTTP_RESOURCE_DESCRIPTION = "http resource description"

@pytest.mark.parametrize("value, expected", [ ("not a float", False), ("3.21", True) ])
def test_is_float_given_a_string_should_return_as_expected(value: str, expected: bool):
    result = utils.is_float(value)

    assert result == expected

def test_http_get_given_a_url_should_get_the_json(monkeypatch: MonkeyPatch, url: str):
    MOCK_RESPONSE = MockHttpResponse()
    def mock_get(url: str, headers: dict):
        MOCK_RESPONSE.json_response["url"] = url
        MOCK_RESPONSE.json_response["headers"] = headers
        return MOCK_RESPONSE
    monkeypatch.setattr(requests, requests.get.__name__, mock_get)

    response = utils.http_get(url, None)

    assert response == MOCK_RESPONSE.json_response
    assert response["url"] == url
    assert response["headers"] == _HEADERS

def test_http_get_given_two_requests_on_the_same_url_should_return_the_cached_value(monkeypatch: MonkeyPatch, url: str):
    MOCK_RESPONSE = MockHttpResponse()
    MOCK_RESPONSE.json_response["counter"] = 0
    def mock_get(url, headers):
        MOCK_RESPONSE.json_response["counter"] += 1
        return MOCK_RESPONSE
    monkeypatch.setattr(requests, requests.get.__name__, mock_get)
    
    _ = utils.http_get(url, None)
    response = utils.http_get(url, None)

    assert response["counter"] == 1

def test_http_get_given_an_http_error_should_raise(monkeypatch: MonkeyPatch, url: str):
    HTTP_ERROR = HTTPError()
    EXPECTED_ERROR = _HTTP_ERROR.format(HTTP_RESOURCE_DESCRIPTION, HTTP_ERROR)
    def mock_get(url, headers):
        raise HTTP_ERROR
    monkeypatch.setattr(requests, requests.get.__name__, mock_get)
    
    with pytest.raises(GeneratorError) as error:
        _ = utils.http_get(url, HTTP_RESOURCE_DESCRIPTION)

    assert error.value.message == EXPECTED_ERROR

@pytest.mark.parametrize("error_to_raise", [ ConnectTimeout, ReadTimeout, Timeout, requests.ConnectionError ])
def test_http_get_given_a_connection_error_should_raise(
    monkeypatch: MonkeyPatch, url: str, error_to_raise: Exception):
    EXPECTED_ERROR = _CONNECTION_ERROR.format(HTTP_RESOURCE_DESCRIPTION)
    def mock_get(url, headers):
        raise error_to_raise
    monkeypatch.setattr(requests, requests.get.__name__, mock_get)
    
    with pytest.raises(GeneratorError) as error:
        _ = utils.http_get(url, HTTP_RESOURCE_DESCRIPTION)

    assert error.value.message == EXPECTED_ERROR