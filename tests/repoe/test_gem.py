import pytest
from repoe import gem
from repoe.constants import Field
from pytest import MonkeyPatch
from test_utilities import WebGetMock

_METADATA_ID = "gem/id"
_GEM_NAME = "gem name"
_BASE_GEM_NAME = "base gem name"

@pytest.fixture(autouse=True)
def get_mock(monkeypatch: MonkeyPatch):
    return WebGetMock(monkeypatch, None)

@pytest.mark.parametrize("base_metadata_id, gem_name, expected", [
    (_METADATA_ID, _BASE_GEM_NAME, True),
    ("another_gem_id", _GEM_NAME, False),
    (_METADATA_ID, _GEM_NAME, False)
])
def test_is_base_gem_given_a_metadata_id_should_return_accordingly(
    get_mock: WebGetMock, base_metadata_id: str, gem_name: str, expected: bool):

    GEMS = _create_gems(base_metadata_id=base_metadata_id, name=gem_name)
    get_mock.result = GEMS

    actual = gem.is_base_gem(_METADATA_ID)

    assert actual == expected

def test_try_get_gem_base_given_a_valid_name_should_return_it(get_mock: WebGetMock):
    GEMS = _create_gems()
    get_mock.result = GEMS

    result = gem.try_get_gem_base(_GEM_NAME)

    assert result == _BASE_GEM_NAME

def test_try_get_gem_base_given_name_not_found_should_return_None(get_mock: WebGetMock):
    get_mock.result = {}

    result = gem.try_get_gem_base(_GEM_NAME)

    assert result == None

@pytest.mark.parametrize("field_to_delete", [ Field.DISPLAY_NAME, Field.BASE_ITEM ])
def test_try_get_gem_base_given_gem_info_is_incomplete_should_ignore_those_gems(
    get_mock: WebGetMock, field_to_delete: Field):

    get_mock.result = _create_gems()
    del get_mock.result["gem"][field_to_delete.value]

    result = gem.try_get_gem_base(_GEM_NAME)

    assert result == None

def _create_gems(
    base_metadata_id: str = _METADATA_ID,
    name: str = _GEM_NAME,
    base_name: str = _BASE_GEM_NAME):
    return {
        "gem": {
            Field.DISPLAY_NAME.value: name,
            Field.BASE_ITEM.value: {
                Field.ID.value: base_metadata_id,
                Field.DISPLAY_NAME.value: base_name
            }
        }
    }