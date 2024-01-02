import repoe, pytest
from pytest import MonkeyPatch
from core import ExpectedError
from test_utilities import WebGetMock
from repoe.functions import _BASE_NAME_NOT_FOUND_ERROR, _BASE_TYPE_CLASS_FIELD, _BASE_TYPE_DOMAIN_FIELD, _NAME_FIELD, _BASE_TYPE_RELEASE_STATE, _RELEASED_BASE_TYPE_RELEASE_STATE, _UNIQUE_ONLY_RELEASE_STATE

_ITEM_CLASS = {
    _NAME_FIELD: "item_class"
}
_BASE_TYPE = {
    _NAME_FIELD: "base name",
    _BASE_TYPE_DOMAIN_FIELD: "domain",
    _BASE_TYPE_CLASS_FIELD: "item_class_id",
    _BASE_TYPE_RELEASE_STATE: _RELEASED_BASE_TYPE_RELEASE_STATE,
}
_UNIQUE_ONLY_BASE_TYPE = {
    _NAME_FIELD: "unique only base name",
    _BASE_TYPE_DOMAIN_FIELD: "domain",
    _BASE_TYPE_CLASS_FIELD: "item_class_id",
    _BASE_TYPE_RELEASE_STATE: _UNIQUE_ONLY_RELEASE_STATE,
}

_BASE_TYPES = {
    "base/type/id": _BASE_TYPE,
    "base/type/unique_only_id": _UNIQUE_ONLY_BASE_TYPE
}
_ITEM_CLASSES = { _BASE_TYPE[_BASE_TYPE_CLASS_FIELD]: _ITEM_CLASS }

@pytest.fixture(autouse=True)
def setup(monkeypatch: MonkeyPatch):
    _ = WebGetMock(monkeypatch, (x for x in [ _BASE_TYPES, _ITEM_CLASSES ]))

@pytest.mark.parametrize("base_name", [
    _BASE_TYPE[_NAME_FIELD],
    _UNIQUE_ONLY_BASE_TYPE[_NAME_FIELD]
])
def test_get_class_for_base_given_a_base_name_should_return_its_class(base_name: str):
    result = repoe.get_class_for_base(base_name)

    assert result == _ITEM_CLASS[_NAME_FIELD]

def test_get_class_for_base_given_the_base_name_is_part_should_use_the_full_name():
    INCOMPLETE_BASE_NAME = _BASE_TYPE[_NAME_FIELD][:2] # first 2 characters taken arbitrarily

    result = repoe.get_class_for_base(INCOMPLETE_BASE_NAME, prefix=True)

    assert result == _ITEM_CLASS[_NAME_FIELD]

@pytest.mark.parametrize("is_part", [ True, False ])
def test_get_class_for_base_given_it_is_not_found_should_raise(is_part: bool):
    INVALID_BASE_TYPE_NAME = "invalid base type name"

    with pytest.raises(ExpectedError) as error:
        _ = repoe.get_class_for_base(INVALID_BASE_TYPE_NAME, is_part)

    assert error.value.message == _BASE_NAME_NOT_FOUND_ERROR.format(INVALID_BASE_TYPE_NAME)