import pytest, ninja, web, repoe
from pytest import MonkeyPatch
from core import CLASS, LINKED_SOCKETS, REPLICA, GREATER, LESS
from ninja import common, CurrencyType, MiscItemType
from ninja.currency import _BASE_TYPE_FIELD as _CURRENCY_BASE_TYPE_FIELD, _VALUE_FIELD as _CURRENCY_VALUE_FIELD, _INVALID_FRAGMENT_BASE_TYPES, _URL as CURRENCY_URL
from ninja.item import _REPLICA_NAME_EXCEPTIONS, LINKS_FIELD, _NAME_FIELD as _ITEM_NAME_FIELD, BASE_TYPE_FIELD as _ITEM_BASE_TYPE_FIELD, _REPLICA_UNIQUE_PREFIX, _UNIQUE_ITEM_TYPES, _VALUE_FIELD as _ITEM_VALUE_FIELD, _URL as _ITEM_URL
from test_utilities import FunctionMock, WebGetMock, create_sieve_for_pattern, create_sieve_for_text

_LEAGUE_NAME = "league_name"
_LOWER_BOUND = 0
_UPPER_BOUND = 5
_CURRENCY_TYPE = CurrencyType.BASIC
_ITEM_TYPE = MiscItemType.ESSENCE
_ITEM_CLASS = "item class"

@pytest.fixture(autouse=True)
def get_class_for_base_mock(monkeypatch: MonkeyPatch):
    return FunctionMock(monkeypatch, repoe.get_class_for_base, _ITEM_CLASS)

def test_get_currency_base_types_given_a_valid_record_was_found_should_return_it(monkeypatch: MonkeyPatch):
    REQUEST_RESULT, EXPECTED = _get_ninja_response(_CURRENCY_BASE_TYPE_FIELD, _CURRENCY_VALUE_FIELD)
    get_mock = WebGetMock(monkeypatch, REQUEST_RESULT)

    base_types = ninja.get_currency_base_types(_LEAGUE_NAME, _CURRENCY_TYPE, _LOWER_BOUND, _UPPER_BOUND)

    assert len(base_types) == 1
    assert EXPECTED[_CURRENCY_BASE_TYPE_FIELD] in base_types
    assert get_mock.received(
        CURRENCY_URL.format(_LEAGUE_NAME, _CURRENCY_TYPE.value),
        expiration=web.Expiration.DAILY)

def test_get_currency_base_types_given_invalid_fragment_base_type_was_found_should_not_return_it(
    monkeypatch: MonkeyPatch):

    REQUEST_RESULT, EXPECTED_TO_FAIL = _get_ninja_response(_CURRENCY_BASE_TYPE_FIELD, _CURRENCY_VALUE_FIELD)
    EXPECTED_TO_FAIL[_CURRENCY_BASE_TYPE_FIELD] = _INVALID_FRAGMENT_BASE_TYPES[0]
    _ = WebGetMock(monkeypatch, REQUEST_RESULT)

    base_types = ninja.get_currency_base_types(_LEAGUE_NAME, _CURRENCY_TYPE, _LOWER_BOUND, _UPPER_BOUND)

    assert len(base_types) == 0

def test_get_misc_base_types_given_a_valid_record_was_found_should_return_it(monkeypatch: MonkeyPatch):
    REQUEST_RESULT, EXPECTED = _get_ninja_response(_ITEM_BASE_TYPE_FIELD, _ITEM_VALUE_FIELD)
    get_mock = WebGetMock(monkeypatch, REQUEST_RESULT)

    base_types = ninja.get_misc_base_types(_LEAGUE_NAME, _ITEM_TYPE, _LOWER_BOUND, _UPPER_BOUND)

    assert len(base_types) == 1
    assert EXPECTED[_ITEM_NAME_FIELD] in base_types
    assert get_mock.received(
        _ITEM_URL.format(_LEAGUE_NAME, _ITEM_TYPE.value),
        expiration=web.Expiration.DAILY)

def test_get_unique_base_types_given_an_empty_unique_filter_should_return_a_valid_record(monkeypatch: MonkeyPatch):
    REQUEST_RESULT, EXPECTED = _get_ninja_response(_ITEM_BASE_TYPE_FIELD, _ITEM_VALUE_FIELD)
    SIEVE = create_sieve_for_pattern({})
    get_mock = WebGetMock(monkeypatch, REQUEST_RESULT)

    base_types = ninja.get_unique_base_types(_LEAGUE_NAME, SIEVE, _LOWER_BOUND, _UPPER_BOUND)

    assert len(base_types) == 1
    assert EXPECTED[_ITEM_BASE_TYPE_FIELD] in base_types
    for unique_item_type in _UNIQUE_ITEM_TYPES:
        assert get_mock.received(_ITEM_URL.format(_LEAGUE_NAME, unique_item_type))

def test_get_unique_base_types_given_record_has_a_required_class_should_return_it(monkeypatch: MonkeyPatch):
    REQUEST_RESULT, EXPECTED = _get_ninja_response(_ITEM_BASE_TYPE_FIELD, _ITEM_VALUE_FIELD)
    SIEVE = create_sieve_for_pattern({ CLASS: f'"{_ITEM_CLASS}"' })
    _ = WebGetMock(monkeypatch, REQUEST_RESULT)
    
    base_types = ninja.get_unique_base_types(_LEAGUE_NAME, SIEVE, _LOWER_BOUND, _UPPER_BOUND)

    assert len(base_types) == 1
    assert EXPECTED[_ITEM_BASE_TYPE_FIELD] in base_types

def test_get_unique_base_types_given_record_has_no_matching_class_should_not_return_it(monkeypatch: MonkeyPatch):
    REQUEST_RESULT, _ = _get_ninja_response(_ITEM_BASE_TYPE_FIELD, _ITEM_VALUE_FIELD)
    SIEVE = create_sieve_for_pattern({ CLASS: "unknown_class" })
    _ = WebGetMock(monkeypatch, REQUEST_RESULT)

    base_types = ninja.get_unique_base_types(_LEAGUE_NAME, SIEVE, _LOWER_BOUND, _UPPER_BOUND)

    assert len(base_types) == 0

@pytest.mark.parametrize("replica", [ True, False ])
def test_get_unique_base_types_given_replica_match_on_record_and_filter_should_return_it(
    monkeypatch: MonkeyPatch, replica: bool):
    
    REQUEST_RESULT, EXPECTED = _get_ninja_response(_ITEM_BASE_TYPE_FIELD, _ITEM_VALUE_FIELD)
    EXPECTED[_ITEM_NAME_FIELD] = _REPLICA_UNIQUE_PREFIX if replica else ""
    SIEVE = create_sieve_for_pattern({ REPLICA: replica })
    _ = WebGetMock(monkeypatch, REQUEST_RESULT)

    base_types = ninja.get_unique_base_types(_LEAGUE_NAME, SIEVE, _LOWER_BOUND, _UPPER_BOUND)

    assert len(base_types) == 1
    assert EXPECTED[_ITEM_BASE_TYPE_FIELD] in base_types

@pytest.mark.parametrize("replica", [ True, False ])
def test_get_unique_base_types_given_replica_mismatch_on_record_and_filter_should_not_return_it(
    monkeypatch: MonkeyPatch, replica: bool):
    
    REQUEST_RESULT, EXPECTED = _get_ninja_response(_ITEM_BASE_TYPE_FIELD, _ITEM_VALUE_FIELD)
    EXPECTED[_ITEM_NAME_FIELD] = _REPLICA_UNIQUE_PREFIX if replica else ""
    SIEVE = create_sieve_for_pattern({ REPLICA: not replica })
    _ = WebGetMock(monkeypatch, REQUEST_RESULT)

    base_types = ninja.get_unique_base_types(_LEAGUE_NAME, SIEVE, _LOWER_BOUND, _UPPER_BOUND)

    assert len(base_types) == 0

def test_get_unique_base_types_given_replica_name_exception_should_return_it_when_replica_is_set_to_false(
    monkeypatch: MonkeyPatch):

    REQUEST_RESULT, EXPECTED = _get_ninja_response(_ITEM_BASE_TYPE_FIELD, _ITEM_VALUE_FIELD)
    EXPECTED[_ITEM_NAME_FIELD] = _REPLICA_NAME_EXCEPTIONS[0]
    SIEVE = create_sieve_for_pattern({ REPLICA: False })
    _ = WebGetMock(monkeypatch, REQUEST_RESULT)

    base_types = ninja.get_unique_base_types(_LEAGUE_NAME, SIEVE, _LOWER_BOUND, _UPPER_BOUND)

    assert len(base_types) == 1
    assert EXPECTED[_ITEM_BASE_TYPE_FIELD] in base_types

def test_get_unique_base_types_given_links_in_filter_and_within_bounds_on_record_should_return_it(
    monkeypatch: MonkeyPatch):
    
    LINKS = 3
    REQUEST_RESULT, EXPECTED = _get_ninja_response(_ITEM_BASE_TYPE_FIELD, _ITEM_VALUE_FIELD)
    EXPECTED[LINKS_FIELD] = LINKS
    SIEVE = create_sieve_for_text(
    f"""{LINKED_SOCKETS} {GREATER} {LINKS - 1}
        {LINKED_SOCKETS} {LESS} {LINKS + 1}""")
    _ = WebGetMock(monkeypatch, REQUEST_RESULT)

    base_types = ninja.get_unique_base_types(_LEAGUE_NAME, SIEVE, _LOWER_BOUND, _UPPER_BOUND)

    assert len(base_types) == 1
    assert EXPECTED[_ITEM_BASE_TYPE_FIELD] in base_types

@pytest.mark.parametrize("actual_links, min_links, max_links", [ (1, 2, 3), (4, 2, 3) ])
def test_get_unique_base_types_given_links_in_filter_and_out_of_bounds_links_on_record_should_not_return_it(
    monkeypatch: MonkeyPatch, actual_links: int, min_links: int, max_links: int):
    
    REQUEST_RESULT, EXPECTED = _get_ninja_response(_ITEM_BASE_TYPE_FIELD, _ITEM_VALUE_FIELD)
    EXPECTED[LINKS_FIELD] = actual_links
    SIEVE = create_sieve_for_text(
    f"""{LINKED_SOCKETS} {GREATER} {min_links}
        {LINKED_SOCKETS} {LESS} {max_links}""")
    _ = WebGetMock(monkeypatch, REQUEST_RESULT)

    base_types = ninja.get_unique_base_types(_LEAGUE_NAME, SIEVE, _LOWER_BOUND, _UPPER_BOUND)

    assert len(base_types) == 0

def test_get_unique_base_types_given_no_links_on_record_should_set_links_on_record_to_0(
    monkeypatch: MonkeyPatch):
    
    REQUEST_RESULT, EXPECTED = _get_ninja_response(_ITEM_BASE_TYPE_FIELD, _ITEM_VALUE_FIELD)
    SIEVE = create_sieve_for_pattern({ LINKED_SOCKETS: 1 })
    _ = WebGetMock(monkeypatch, REQUEST_RESULT)

    _ = ninja.get_unique_base_types(_LEAGUE_NAME, SIEVE, _LOWER_BOUND, _UPPER_BOUND)

    assert EXPECTED[LINKS_FIELD] == 0

def _get_ninja_response(base_type_field_name: str, value_field_name: str):
    below_bound_record = {
        _ITEM_NAME_FIELD: "below bound base item name",
        base_type_field_name: "below bound base type",
        value_field_name: _LOWER_BOUND - 1
    }
    within_bound_record = {
        _ITEM_NAME_FIELD: "within bound base item name",
        base_type_field_name: "within bound base type",
        value_field_name: (_LOWER_BOUND + _UPPER_BOUND) / 2
    }
    above_bound_record = {
        _ITEM_NAME_FIELD: "above bound base item name",
        base_type_field_name: "above bound base type",
        value_field_name: _UPPER_BOUND + 1
    }
    response = {
        common._RECORD_LINES_FIELD: [
            below_bound_record,
            within_bound_record,
            above_bound_record
        ]
    }
    return (response, within_bound_record)