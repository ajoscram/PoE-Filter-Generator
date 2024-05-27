import pytest
from pytest import MonkeyPatch
from repoe import class_, base, base_validation, gem
from repoe.constants import *
from repoe.base_validation import _ReleaseState
from repoe.base import _BASE_NAME_NOT_FOUND_ERROR
from core import ExpectedError, CLASS, BASE_TYPE, DROP_LEVEL, ITEM_LEVEL, EQUALS
from test_utilities import create_sieve_for_text, WebGetMock, FunctionMock

_BASE_NAME = "base_name"
_CLASS_ID = "class_id"
_FILTER_CLASS_NAME = "filter_item_class"
_DOMAIN_NAME = "domain"
_TAG = "tag"
_LEVEL = 12 # chosen arbitrarily

@pytest.fixture(autouse=True)
def get_mock(monkeypatch: MonkeyPatch):
    return WebGetMock(monkeypatch, None)

@pytest.fixture(autouse=True)
def class_mock(monkeypatch: MonkeyPatch):
    return FunctionMock(monkeypatch, class_.get_filter_item_class, _FILTER_CLASS_NAME, target=class_)

@pytest.fixture(autouse=True)
def base_validation_mock(monkeypatch: MonkeyPatch):
    return FunctionMock(monkeypatch, base_validation.validate, True, target=base_validation)

@pytest.fixture(autouse=True)
def try_get_gem_base_mock(monkeypatch: MonkeyPatch):
    return FunctionMock(monkeypatch, gem.try_get_gem_base, target=gem)

def test_get_bases_given_a_sieve_should_return_bases_that_match_it(get_mock: WebGetMock):
    BASE_TYPES = _create_bases()
    SIEVE = _create_sieve(BASE_TYPES, _FILTER_CLASS_NAME)
    get_mock.result = BASE_TYPES

    result = base.get_bases(SIEVE)

    assert len(result) == 1
    assert _BASE_NAME in result

def test_get_class_for_base_given_a_base_name_should_return_its_class(get_mock: WebGetMock):
    get_mock.result = _create_bases()

    result = base.get_class_for_base(_BASE_NAME)

    assert result == _FILTER_CLASS_NAME

def test_get_class_for_base_given_a_transfigured_gem_base_name_should_return_its_class(
    get_mock: WebGetMock, try_get_gem_base_mock: FunctionMock):
    
    BASE_GEM_NAME = "Gem"
    TRANSFIGURED_GEM_NAME = f"{BASE_GEM_NAME} of Transfiguration"
    get_mock.result = _create_bases(name=BASE_GEM_NAME)
    try_get_gem_base_mock.result = BASE_GEM_NAME

    result = base.get_class_for_base(TRANSFIGURED_GEM_NAME)

    assert result == _FILTER_CLASS_NAME

def test_get_class_for_base_given_it_is_not_found_should_raise(get_mock: WebGetMock):
    INVALID_BASE_TYPE_NAME = "invalid base type name"
    get_mock.result = {}

    with pytest.raises(ExpectedError) as error:
        _ = base.get_class_for_base(INVALID_BASE_TYPE_NAME)

    assert error.value.message == _BASE_NAME_NOT_FOUND_ERROR.format(INVALID_BASE_TYPE_NAME)

def test_get_domains_and_tags_given_a_sieve_should_return_domains_and_tags(get_mock: WebGetMock):
    BASE_TYPES = _create_bases()
    SIEVE = _create_sieve(BASE_TYPES, _FILTER_CLASS_NAME)
    get_mock.result = BASE_TYPES

    (domains, tags) = base.get_domains_and_tags(SIEVE)

    assert _DOMAIN_NAME in domains
    assert _TAG in tags

def _create_bases(
    name: str = _BASE_NAME,
    class_id: str = _CLASS_ID,
    domain: str = _DOMAIN_NAME,
    release_state: str = _ReleaseState.RELEASED.value,
    drop_level: int = _LEVEL,
    tag: str = _TAG):
    return {
        "base/type/id": {
            Field.NAME.value: name,
            Field.DOMAIN.value: domain,
            Field.CLASS.value: class_id,
            Field.RELEASE_STATE.value: release_state,
            Field.DROP_LEVEL.value: drop_level,
            Field.TAGS.value: [ tag ]
        }
    }

def _create_sieve(base_types: dict[dict[str]], filter_class_name: str):
    base_type = list(base_types.values())[0]
    text = f"""
        {CLASS} {EQUALS} "{filter_class_name}"
        {BASE_TYPE} {EQUALS} "{base_type[Field.NAME.value]}"
        {DROP_LEVEL} {EQUALS} {base_type[Field.DROP_LEVEL.value]}
        {ITEM_LEVEL} {EQUALS} {base_type[Field.DROP_LEVEL.value]}"""
    return create_sieve_for_text(text)