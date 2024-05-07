import pytest, ninja, repoe
from pytest import MonkeyPatch
from core import REPLICA, LINKED_SOCKETS, CLASS
from ninja.constants import *
from test_utilities import FunctionMock, WebGetMock, create_sieve_for_text, create_sieve_for_pattern
from ninja.validation import _INVALID_FRAGMENT_BASE_TYPES, _REPLICA_ITEM_NAME_EXCEPTIONS

_LEAGUE_NAME = "league_name"
_VALUE = 5
_ITEM_CLASS = "item class"
_BASE_TYPE = "base type"
_DEFAULT_SIEVE = create_sieve_for_text("Show")

@pytest.fixture(autouse=True)
def get_class_for_base_mock(monkeypatch: MonkeyPatch):
    return FunctionMock(monkeypatch, repoe.get_class_for_base, _ITEM_CLASS)

@pytest.fixture(autouse=True)
def web_get_mock(monkeypatch: MonkeyPatch):
    return WebGetMock(monkeypatch, _get_ninja_response())

@pytest.mark.parametrize("query_type", [ QueryType.CURRENCY, QueryType.ESSENCE ])
def test_get_bases_given_a_valid_record_was_found_should_return_it(query_type: QueryType):
    base_types = ninja.get_bases(query_type, _LEAGUE_NAME, _DEFAULT_SIEVE, _VALUE - 1, _VALUE + 1)

    assert _BASE_TYPE in base_types

@pytest.mark.parametrize("value", [ _VALUE - 1, _VALUE + 1 ])
def test_get_bases_given_outside_value_bounds_should_not_return_it(value: int, web_get_mock: WebGetMock):
    web_get_mock.result = _get_ninja_response(value=value)

    base_types = ninja.get_bases(QueryType.CURRENCY, _LEAGUE_NAME, _DEFAULT_SIEVE, _VALUE, _VALUE)

    assert len(base_types) == 0

def test_get_currency_base_types_given_invalid_fragment_base_type_was_found_should_not_return_it(
    web_get_mock: WebGetMock):
    
    web_get_mock.result = _get_ninja_response(base_type=_INVALID_FRAGMENT_BASE_TYPES[0])

    base_types = ninja.get_bases(QueryType.FRAGMENT, _LEAGUE_NAME, _DEFAULT_SIEVE, _VALUE)

    assert len(base_types) == 0

@pytest.mark.parametrize("replica", [ True, False ])
def test_get_bases_given_replica_unique_base_should_return_depending_on_sieve(
    web_get_mock: WebGetMock, replica: bool):
    
    NAME = f"{REPLICA} {_BASE_TYPE}"
    SIEVE = create_sieve_for_pattern({ REPLICA: replica })
    web_get_mock.result = _get_ninja_response(name=NAME)
    
    base_types = ninja.get_bases(QueryType.UNIQUE_ARMOUR, _LEAGUE_NAME, SIEVE, _VALUE)

    assert (_BASE_TYPE in base_types) == replica

@pytest.mark.parametrize("replica", [ True, False ])
def test_get_bases_given_replica_unique_name_exceptions_should_return_depending_on_sieve(
    web_get_mock: WebGetMock, replica: bool):

    SIEVE = create_sieve_for_pattern({ REPLICA: replica })
    web_get_mock.result = _get_ninja_response(name=_REPLICA_ITEM_NAME_EXCEPTIONS[0])

    base_types = ninja.get_bases(QueryType.UNIQUE_ACCESSORY, _LEAGUE_NAME, SIEVE, _VALUE)

    assert (_BASE_TYPE in base_types) != replica

@pytest.mark.parametrize("links", [ 3, 4 ])
def test_get_bases_given_unique_with_links_should_return_depending_on_sieve(
    web_get_mock: WebGetMock, links: int):
    
    SIEVE_LINKS = 3
    SIEVE = create_sieve_for_pattern({ LINKED_SOCKETS: SIEVE_LINKS })
    web_get_mock.result = _get_ninja_response(links=links)

    base_types = ninja.get_bases(QueryType.UNIQUE_WEAPON, _LEAGUE_NAME, SIEVE, _VALUE)
    
    assert (_BASE_TYPE in base_types) == (links == SIEVE_LINKS)

@pytest.mark.parametrize("class_", [ _ITEM_CLASS, "another class" ])
def test_get_bases_given_unique_with_class_should_return_depending_on_sieve(class_: str):
    SIEVE = create_sieve_for_pattern({ CLASS: f'"{class_}"' })

    base_types = ninja.get_bases(QueryType.UNIQUE_JEWEL, _LEAGUE_NAME, SIEVE, _VALUE)

    assert (_BASE_TYPE in base_types) == (class_ == _ITEM_CLASS)

def _get_ninja_response(
        value: float = None,
        base_type: str = None,
        name: str = None,
        links: int = None):
    
    def response_generator(url: str, expiration, formatter):
        nonlocal value, base_type, name, links
        base_type_field = CURRENCY_BASE_TYPE_FIELD if "currency" in url else ITEM_BASE_TYPE_FIELD
        value_field = CURRENCY_VALUE_FIELD if "currency" in url else ITEM_VALUE_FIELD
        record = {
            value_field: value or _VALUE,
            base_type_field: base_type or _BASE_TYPE,
            ITEM_NAME_FIELD: name or _BASE_TYPE,            
        }

        if (links != None):
            record[LINKS_FIELD] = links

        return { RECORD_LINES_FIELD: [ record ] }
    
    return response_generator