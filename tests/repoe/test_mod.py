import pytest
from pytest import MonkeyPatch
from core import Operand, Operator
from repoe import base, mod
from repoe.constants import Field
from repoe.mod import _VALID_GENERATION_TYPES
from test_utilities import WebGetMock, FunctionMock, create_sieve_for_text

_MOD_NAME = "mod name"
_DOMAIN_NAME = "domain"
_TAG = "mod tag"
_LEVEL = 12 # chosen arbitrarily

@pytest.fixture(autouse=True)
def get_mock(monkeypatch: MonkeyPatch):
    return WebGetMock(monkeypatch, None)


@pytest.fixture(autouse=True)
def get_domains_and_tags_mock(monkeypatch: MonkeyPatch):
    DOMAINS_AND_TAGS = ( { _DOMAIN_NAME }, { _TAG } )
    return FunctionMock(monkeypatch, base.get_domains_and_tags, DOMAINS_AND_TAGS, target=base)

def test_get_mods_given_a_matching_mod_should_return_it(get_mock: WebGetMock):
    MODS = _create_mods()
    SIEVE = _create_sieve()
    get_mock.result = MODS

    mods = mod.get_mods(SIEVE)

    assert len(mods) == 1
    assert _MOD_NAME in mods

@pytest.mark.parametrize("_create_mods_params", [
    { "domain": "some_other_domain" },
    { "required_level": _LEVEL - 1 },
    { "tag": "some_other_tag" },
    { "weight": 0 },
])
def test_get_mods_given_no_matching_mod_was_found_should_not_return_it(
    get_mock: WebGetMock, _create_mods_params: dict[str]):
    
    MODS = _create_mods(**_create_mods_params)
    SIEVE = _create_sieve()
    get_mock.result = MODS
    
    mods = mod.get_mods(SIEVE)

    assert len(mods) == 0

def _create_mods(
    name: str = _MOD_NAME,
    domain: str = _DOMAIN_NAME,
    generation_type: str = _VALID_GENERATION_TYPES[0],
    required_level: int = _LEVEL,
    tag: str = _TAG,
    weight: int = 1):
    return {
        "mod/id": {
            Field.NAME: name,
            Field.DOMAIN: domain,
            Field.GENERATION_TYPE: generation_type,
            Field.REQUIRED_LEVEL: required_level,
            Field.SPAWN_WEIGHTS: [
                {
                    Field.TAG: tag,
                    Field.WEIGHT: weight
                }
            ]
        }
    }

def _create_sieve():
    text = f"{Operand.ITEM_LEVEL} {Operator.EQUALS} {_LEVEL}"
    return create_sieve_for_text(text)