import pytest, web, requests
from test_utilities import FunctionMock
from pytest import MonkeyPatch
from requests import ConnectTimeout, HTTPError, ReadTimeout, Timeout, ConnectionError
from web.functions import _HEADERS, _HTTP_ERROR as _HTTP_ERROR_TEXT, _CONNECTION_ERROR
from core import ExpectedError

class _MockHttpResponse:
    def __init__(self):
        self.json_response = { "some": "json" }
        self.text = str(self.json_response)
        self.status_code = 1
    
    def raise_for_status(self):
        pass
    
    def json(self):
        return self.json_response

_MOCK_RESPONSE = _MockHttpResponse()
_HTTP_ERROR = HTTPError(response=_MOCK_RESPONSE)
_URL = "url"

@pytest.fixture(autouse=True)
def setup():
    web.functions._get_cache = {}

def test_get_given_a_url_should_get_the_json(monkeypatch: MonkeyPatch):
    get_mock = FunctionMock(monkeypatch, requests.get, _MOCK_RESPONSE)

    response = web.get(_URL)

    assert get_mock.received(_URL, headers=_HEADERS)
    assert response == _MOCK_RESPONSE.json_response

def test_get_given_json_flag_is_false_should_return_the_text_instead(monkeypatch: MonkeyPatch):
    _ = FunctionMock(monkeypatch, requests.get, _MOCK_RESPONSE)

    response = web.get(_URL, json=False)

    assert response == _MOCK_RESPONSE.text

def test_get_given_multiple_requests_on_the_same_url_should_return_the_cached_value(monkeypatch: MonkeyPatch):
    get_mock = FunctionMock(monkeypatch, requests.get, _MOCK_RESPONSE)

    _ = web.get(_URL)
    _ = web.get(_URL)

    assert get_mock.get_invocation_count() == 1 # when the cache is hit only one request is expected

def test_get_given_an_http_error_should_raise(monkeypatch: MonkeyPatch):
    _ = FunctionMock(monkeypatch, requests.get, _HTTP_ERROR)
    
    with pytest.raises(ExpectedError) as error:
        _ = web.get(_URL)

    assert error.value.message == _HTTP_ERROR_TEXT.format(_URL, _HTTP_ERROR)

def test_get_given_a_custom_http_error_should_raise_with_it_instead(monkeypatch: MonkeyPatch):
    CUSTOM_ERROR_MESSAGE = "custom error message"
    _ = FunctionMock(monkeypatch, requests.get, _HTTP_ERROR)

    with pytest.raises(ExpectedError) as error:
        _ = web.get(_URL, custom_http_errors={ _MOCK_RESPONSE.status_code: CUSTOM_ERROR_MESSAGE })

    assert error.value.message == CUSTOM_ERROR_MESSAGE

@pytest.mark.parametrize("error_to_raise", [ ConnectTimeout, ReadTimeout, Timeout, ConnectionError ])
def test_get_given_a_connection_error_should_raise(monkeypatch: MonkeyPatch, error_to_raise: Exception):
    _ = FunctionMock(monkeypatch, requests.get, error_to_raise)
    
    with pytest.raises(ExpectedError) as error:
        _ = web.get(_URL)

    assert error.value.message == _CONNECTION_ERROR.format(_URL)