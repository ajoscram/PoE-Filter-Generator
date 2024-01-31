import repoe, pytest
from pytest import MonkeyPatch
from test_utilities import WebGetMock, create_sieve_for_pattern
from core import ExpectedError, CLASS, BASE_TYPE, DROP_LEVEL, ITEM_LEVEL
from repoe.constants import NAME_FIELD, DOMAIN_FIELD
from repoe.base import _TAGS_FIELD, _DROP_LEVEL_FIELD, _BASE_NAME_NOT_FOUND_ERROR, _CLASS_FIELD, _RELEASE_STATE_FIELD, _RELEASED_RELEASE_STATE, _UNIQUE_ONLY_RELEASE_STATE
from repoe.mod import _WEIGHT_FIELD, _TAG_FIELD, _SPAWN_WEIGHTS_FIELD, _REQUIRED_LEVEL_FIELD, _VALID_GENERATION_TYPES, _GENERATION_TYPE_FIELD

_MOD_NAME = "mod name"
_BASE_NAME = "base_name"
_CLASS_ID = "class_id"
_CLASS_NAME = "class_name"
_DOMAIN_NAME = "domain"
_TAG = "tag"
_LEVEL = 12 # chosen arbitrarily

def test_get_bases_given_a_sieve_should_return_bases_that_match_it(monkeypatch: MonkeyPatch):
    ITEM_CLASSES = _create_item_classes()
    BASE_TYPES = _create_bases()
    PATTERN = _create_sieve_pattern(BASE_TYPES, _CLASS_NAME)
    SIEVE = create_sieve_for_pattern(PATTERN)
    _ = WebGetMock(monkeypatch, (x for x in [ BASE_TYPES, ITEM_CLASSES ]))

    result = repoe.get_bases(SIEVE)

    assert len(result) == 1
    assert _BASE_NAME in result

@pytest.mark.parametrize("release_state", [_RELEASED_RELEASE_STATE, _UNIQUE_ONLY_RELEASE_STATE])
def test_get_class_for_base_should_return_its_class(monkeypatch: MonkeyPatch, release_state: str):
    ITEM_CLASSES = _create_item_classes()
    BASE_TYPES = _create_bases(release_state=release_state)
    _ = WebGetMock(monkeypatch, (x for x in [ BASE_TYPES, ITEM_CLASSES ]))
    
    result = repoe.get_class_for_base(_BASE_NAME)

    assert result == _CLASS_NAME

def test_get_class_for_base_given_it_is_not_found_should_raise(monkeypatch: MonkeyPatch):
    INVALID_BASE_TYPE_NAME = "invalid base type name"
    ITEM_CLASSES = _create_item_classes()
    BASE_TYPES = _create_bases(class_id=_CLASS_ID)
    _ = WebGetMock(monkeypatch, (x for x in [ BASE_TYPES, ITEM_CLASSES ]))

    with pytest.raises(ExpectedError) as error:
        _ = repoe.get_class_for_base(INVALID_BASE_TYPE_NAME)

    assert error.value.message == _BASE_NAME_NOT_FOUND_ERROR.format(INVALID_BASE_TYPE_NAME)

def test_get_mods_given_a_matching_mod_should_return_it(monkeypatch: MonkeyPatch):
    ITEM_CLASSES = _create_item_classes()
    BASE_TYPES = _create_bases()
    MODS = _create_mods()
    PATTERN = _create_sieve_pattern(BASE_TYPES, _CLASS_NAME)
    SIEVE = create_sieve_for_pattern(PATTERN)
    _ = WebGetMock(monkeypatch, (x for x in [ MODS, BASE_TYPES, ITEM_CLASSES ]))

    mods = repoe.get_mods(SIEVE)

    assert len(mods) == 1
    assert _MOD_NAME in mods

@pytest.mark.parametrize("_create_mods_params", [
    { "domain": "some_other_domain" },
    { "required_level": _LEVEL - 1 },
    { "tag": "some_other_tag" },
    { "weight": 0 },
])
def test_get_mods_given_no_matching_mod_was_found_should_not_return_it(
    monkeypatch: MonkeyPatch, _create_mods_params: dict[str]):
    
    ITEM_CLASSES = _create_item_classes()
    BASE_TYPES = _create_bases()
    MODS = _create_mods(**_create_mods_params)
    PATTERN = _create_sieve_pattern(BASE_TYPES, _CLASS_NAME)
    SIEVE = create_sieve_for_pattern(PATTERN)
    _ = WebGetMock(monkeypatch, (x for x in [ MODS, BASE_TYPES, ITEM_CLASSES ]))

    mods = repoe.get_mods(SIEVE)

    assert len(mods) == 0

def _create_item_classes(id: str = _CLASS_ID, name: str = _CLASS_NAME):
    return { id: { NAME_FIELD: name } }

def _create_bases(
    name: str = _BASE_NAME,
    class_id: str = _CLASS_ID,
    domain: str = _DOMAIN_NAME,
    release_state: str = _RELEASED_RELEASE_STATE,
    drop_level: int = _LEVEL,
    tag: str = _TAG):
    return {
        "base/type/id": {
            NAME_FIELD: name,
            DOMAIN_FIELD: domain,
            _CLASS_FIELD: class_id,
            _RELEASE_STATE_FIELD: release_state,
            _DROP_LEVEL_FIELD: drop_level,
            _TAGS_FIELD: [ tag ]
        }
    }

def _create_mods(
    name: str = _MOD_NAME,
    domain: str = _DOMAIN_NAME,
    generation_type: str = _VALID_GENERATION_TYPES[0],
    required_level: int = _LEVEL,
    tag: str = _TAG,
    weight: int = 1):
    return {
        "mod/id": {
            NAME_FIELD: name,
            DOMAIN_FIELD: domain,
            _GENERATION_TYPE_FIELD: generation_type,
            _REQUIRED_LEVEL_FIELD: required_level,
            _SPAWN_WEIGHTS_FIELD: [
                {
                    _TAG_FIELD: tag,
                    _WEIGHT_FIELD: weight
                }
            ]
        }
    }

def _create_sieve_pattern(base_types: dict[dict[str]], filter_class_name: str):
    base_type = list(base_types.values())[0]
    return {
        CLASS: filter_class_name,
        BASE_TYPE: base_type[NAME_FIELD],
        DROP_LEVEL: base_type[_DROP_LEVEL_FIELD],
        ITEM_LEVEL: base_type[_DROP_LEVEL_FIELD] }