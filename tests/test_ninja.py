import pytest
import ninja
from pytest import MonkeyPatch
from ninja import common, CurrencyType, MiscItemType, UniqueFilter
from ninja.currency import _BASE_TYPE_FIELD as _CURRENCY_BASE_TYPE_FIELD, _VALUE_FIELD as _CURRENCY_VALUE_FIELD, _INVALID_FRAGMENT_BASE_TYPES, _URL as CURRENCY_URL
from ninja.item import _LINKS_FIELD, _NAME_FIELD as _ITEM_NAME_FIELD, _BASE_TYPE_FIELD as _ITEM_BASE_TYPE_FIELD, _REPLICA_UNIQUE_PREFIX, _UNIQUE_ITEM_TYPES, _VALUE_FIELD as _ITEM_VALUE_FIELD, _URL as _ITEM_URL
from tests.test_utilities.http_mock import HttpMock
import wiki

LEAGUE_NAME = "league_name"
LOWER_BOUND = 0
UPPER_BOUND = 5
CURRENCY_TYPE = CurrencyType.BASIC # chosen arbitrarily
ITEM_TYPE = MiscItemType.BEAST # chosen arbitrarily

def test_get_currency_base_types_given_a_valid_record_was_found_should_return_it(monkeypatch: MonkeyPatch):
    REQUEST_RESULT, EXPECTED = _get_ninja_response(_CURRENCY_BASE_TYPE_FIELD, _CURRENCY_VALUE_FIELD)
    http_mock = HttpMock(monkeypatch, REQUEST_RESULT)

    base_types = ninja.get_currency_base_types(LEAGUE_NAME, CURRENCY_TYPE, LOWER_BOUND, UPPER_BOUND)

    assert len(base_types) == 1
    assert base_types[0] == EXPECTED[_CURRENCY_BASE_TYPE_FIELD]
    assert CURRENCY_URL.format(LEAGUE_NAME, CURRENCY_TYPE.value) in http_mock.urls_queried

def test_get_currency_base_types_given_invalid_fragment_base_type_was_found_should_not_return_it(
    monkeypatch: MonkeyPatch):
    REQUEST_RESULT, EXPECTED_TO_FAIL = _get_ninja_response(_CURRENCY_BASE_TYPE_FIELD, _CURRENCY_VALUE_FIELD)
    EXPECTED_TO_FAIL[_CURRENCY_BASE_TYPE_FIELD] = _INVALID_FRAGMENT_BASE_TYPES[0]
    _ = HttpMock(monkeypatch, REQUEST_RESULT)

    base_types = ninja.get_currency_base_types(LEAGUE_NAME, CURRENCY_TYPE, LOWER_BOUND, UPPER_BOUND)

    assert len(base_types) == 0

def test_get_misc_base_types_given_a_valid_record_was_found_should_return_it(monkeypatch: MonkeyPatch):
    REQUEST_RESULT, EXPECTED = _get_ninja_response(_ITEM_NAME_FIELD, _ITEM_VALUE_FIELD)
    http_mock = HttpMock(monkeypatch, REQUEST_RESULT)

    base_types = ninja.get_misc_base_types(LEAGUE_NAME, ITEM_TYPE, LOWER_BOUND, UPPER_BOUND)

    assert len(base_types) == 1
    assert base_types[0] == EXPECTED[_ITEM_NAME_FIELD]
    assert _ITEM_URL.format(LEAGUE_NAME, ITEM_TYPE.value) in http_mock.urls_queried

def test_get_unique_base_types_given_an_empty_unique_filter_should_return_a_valid_record(monkeypatch: MonkeyPatch):
    REQUEST_RESULT, EXPECTED = _get_ninja_response(_ITEM_BASE_TYPE_FIELD, _ITEM_VALUE_FIELD)
    http_mock = HttpMock(monkeypatch, REQUEST_RESULT)

    base_types = ninja.get_unique_base_types(LEAGUE_NAME, UniqueFilter(), LOWER_BOUND, UPPER_BOUND)

    assert len(base_types) == 1
    assert base_types[0] == EXPECTED[_ITEM_BASE_TYPE_FIELD]
    for unique_item_type in _UNIQUE_ITEM_TYPES:
        assert _ITEM_URL.format(LEAGUE_NAME, unique_item_type) in http_mock.urls_queried

def test_get_unique_base_types_given_record_has_a_required_class_should_return_it(
    monkeypatch: MonkeyPatch):
    CLASS = "class"
    UNIQUE_FILTER = UniqueFilter()
    UNIQUE_FILTER.classes = [ CLASS ]
    REQUEST_RESULT, EXPECTED = _get_ninja_response(_ITEM_BASE_TYPE_FIELD, _ITEM_VALUE_FIELD)
    monkeypatch.setattr(wiki, wiki.get_class_id_for_base_type.__name__, lambda _: CLASS)
    _ = HttpMock(monkeypatch, REQUEST_RESULT)

    base_types = ninja.get_unique_base_types(LEAGUE_NAME, UNIQUE_FILTER, LOWER_BOUND, UPPER_BOUND)

    assert len(base_types) == 1
    assert base_types[0] == EXPECTED[_ITEM_BASE_TYPE_FIELD]

def test_get_unique_base_types_given_record_has_no_matching_class_should_not_return_it(monkeypatch: MonkeyPatch):
    UNIQUE_FILTER = UniqueFilter()
    UNIQUE_FILTER.classes = []
    REQUEST_RESULT, _ = _get_ninja_response(_ITEM_BASE_TYPE_FIELD, _ITEM_VALUE_FIELD)
    monkeypatch.setattr(wiki, wiki.get_class_id_for_base_type.__name__, lambda _: "class")
    _ = HttpMock(monkeypatch, REQUEST_RESULT)

    base_types = ninja.get_unique_base_types(LEAGUE_NAME, UNIQUE_FILTER, LOWER_BOUND, UPPER_BOUND)

    assert len(base_types) == 0

@pytest.mark.parametrize("replica", [ True, False ])
def test_get_unique_base_types_given_replica_match_on_record_and_filter_should_return_it(
    monkeypatch: MonkeyPatch, replica: bool):
    REQUEST_RESULT, EXPECTED = _get_ninja_response(_ITEM_BASE_TYPE_FIELD, _ITEM_VALUE_FIELD)
    EXPECTED[_ITEM_NAME_FIELD] = _REPLICA_UNIQUE_PREFIX if replica else ""
    UNIQUE_FILTER = UniqueFilter()
    UNIQUE_FILTER.is_replica = replica
    _ = HttpMock(monkeypatch, REQUEST_RESULT)

    base_types = ninja.get_unique_base_types(LEAGUE_NAME, UNIQUE_FILTER, LOWER_BOUND, UPPER_BOUND)

    assert len(base_types) == 1
    assert base_types[0] == EXPECTED[_ITEM_BASE_TYPE_FIELD]

@pytest.mark.parametrize("replica", [ True, False ])
def test_get_unique_base_types_given_replica_mismatch_on_record_and_filter_should_not_return_it(
    monkeypatch: MonkeyPatch, replica: bool):
    REQUEST_RESULT, EXPECTED = _get_ninja_response(_ITEM_BASE_TYPE_FIELD, _ITEM_VALUE_FIELD)
    EXPECTED[_ITEM_NAME_FIELD] = _REPLICA_UNIQUE_PREFIX if replica else ""
    UNIQUE_FILTER = UniqueFilter()
    UNIQUE_FILTER.is_replica = not replica
    _ = HttpMock(monkeypatch, REQUEST_RESULT)

    base_types = ninja.get_unique_base_types(LEAGUE_NAME, UNIQUE_FILTER, LOWER_BOUND, UPPER_BOUND)

    assert len(base_types) == 0

def test_get_unique_base_types_given_links_in_filter_and_within_bounds_on_record_should_return_it(
    monkeypatch: MonkeyPatch):
    LINKS = 3
    REQUEST_RESULT, EXPECTED = _get_ninja_response(_ITEM_BASE_TYPE_FIELD, _ITEM_VALUE_FIELD)
    EXPECTED[_LINKS_FIELD] = LINKS
    UNIQUE_FILTER = UniqueFilter()
    UNIQUE_FILTER.min_links = LINKS - 1
    UNIQUE_FILTER.max_links = LINKS + 1
    _ = HttpMock(monkeypatch, REQUEST_RESULT)

    base_types = ninja.get_unique_base_types(LEAGUE_NAME, UNIQUE_FILTER, LOWER_BOUND, UPPER_BOUND)

    assert len(base_types) == 1
    assert base_types[0] == EXPECTED[_ITEM_BASE_TYPE_FIELD]

def test_get_unique_base_types_given_links_in_filter_and_below_min_links_on_record_should_not_return_it(
    monkeypatch: MonkeyPatch):
    LINKS = 3
    REQUEST_RESULT, EXPECTED = _get_ninja_response(_ITEM_BASE_TYPE_FIELD, _ITEM_VALUE_FIELD)
    EXPECTED[_LINKS_FIELD] = LINKS
    UNIQUE_FILTER = UniqueFilter()
    UNIQUE_FILTER.min_links = LINKS + 1
    _ = HttpMock(monkeypatch, REQUEST_RESULT)

    base_types = ninja.get_unique_base_types(LEAGUE_NAME, UNIQUE_FILTER, LOWER_BOUND, UPPER_BOUND)

    assert len(base_types) == 0

def test_get_unique_base_types_given_links_in_filter_and_above_max_links_on_record_should_not_return_it(
    monkeypatch: MonkeyPatch):
    LINKS = 3
    REQUEST_RESULT, EXPECTED = _get_ninja_response(_ITEM_BASE_TYPE_FIELD, _ITEM_VALUE_FIELD)
    EXPECTED[_LINKS_FIELD] = LINKS
    UNIQUE_FILTER = UniqueFilter()
    UNIQUE_FILTER.max_links = LINKS - 1
    _ = HttpMock(monkeypatch, REQUEST_RESULT)

    base_types = ninja.get_unique_base_types(LEAGUE_NAME, UNIQUE_FILTER, LOWER_BOUND, UPPER_BOUND)

    assert len(base_types) == 0

def test_get_unique_base_types_given_links_in_filter_and_no_links_on_record_should_set_links_on_record_to_0(
    monkeypatch: MonkeyPatch):
    REQUEST_RESULT, EXPECTED = _get_ninja_response(_ITEM_BASE_TYPE_FIELD, _ITEM_VALUE_FIELD)
    UNIQUE_FILTER = UniqueFilter()
    UNIQUE_FILTER.min_links = 1
    _ = HttpMock(monkeypatch, REQUEST_RESULT)

    _ = ninja.get_unique_base_types(LEAGUE_NAME, UNIQUE_FILTER, LOWER_BOUND, UPPER_BOUND)

    assert EXPECTED[_LINKS_FIELD] == 0

def _get_ninja_response(base_type_field_name: str, value_field_name: str):
    below_bound_record = {
        base_type_field_name: "below bound base type",
        value_field_name: LOWER_BOUND - 1
    }
    within_bound_record = {
        base_type_field_name: "within bound base type",
        value_field_name: (LOWER_BOUND + UPPER_BOUND) / 2
    }
    above_bound_record = {
        base_type_field_name: "above bound base type",
        value_field_name: UPPER_BOUND + 1
    }
    response = {
        common._RESPONSE_DATA_LOCATION: [
            below_bound_record,
            within_bound_record,
            above_bound_record
        ]
    }
    return (response, within_bound_record)