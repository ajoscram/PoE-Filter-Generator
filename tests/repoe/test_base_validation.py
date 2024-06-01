import pytest
from pytest import MonkeyPatch
from repoe import base_validation, gem
from repoe.constants import Field
from repoe.base_validation import _ReleaseState, _BaseTypeName, _UNRECOGNIZED_BASE_ID_ERROR
from test_utilities import FunctionMock

_BASE_NAME = "base_name"

@pytest.fixture(autouse=True)
def is_base_gem_mock(monkeypatch: MonkeyPatch):
    return FunctionMock(monkeypatch, gem.is_base_gem, True, target=gem)

@pytest.mark.parametrize("id_suffix, info, expected", [
    ("MicrotransactionCurrency/item", { }, False),
    ("Currency/RandomFossilOutcome1", { }, False),
    ("Currency/item", { }, True),
    ("Delve/DelveStackableSocketableCurrency1", { }, True),
    ("Delve/item", { }, False),
    ("Maps/MapHarbingerMid", { }, False),
    ("Maps/MapWorldsName", { }, True),
    ("Maps/item", { }, False),
    ("Gems/item", { }, True),
    ("Gems/GemRoyale1", { }, False),
    ("Gems/item", { "release_state": _ReleaseState.UNRELEASED }, False),
    ("Gems/item", { "release_state": _ReleaseState.UNRELEASED, "name": _BaseTypeName.BLADE_TRAP }, True),
    ("Amulets/Talismans/item", { }, True),
    ("Amulets/Talismans/Talisman1_1_2", { }, False),
    ("AtlasUpgrades/ItemPrimordial1", { }, True),
    ("AtlasUpgrades/item", { }, False),
    ("MapFragments/item", { }, True),
    ("MapFragments/VaalFragment1", { }, False),
    ("MapFragments/Maven/ItemAtlas1", { }, True),
    ("MapFragments/Maven/item", { }, False),
    ("Weapons/item", { }, True),
    ("Weapons/item", { "name": _BaseTypeName.ENERGY_BLADE }, False),
    ("Quivers/item", { }, True),
    ("Quivers/Quiver1", { }, False),
    ("category/item", { }, True),
    ("category/itemRoyale", { }, False),
    ("category/item", { "release_state": _ReleaseState.UNRELEASED }, False),
])
def test_validate_given_a_base_id_and_info_should_return_expectedly(
    id_suffix: str, info: dict[str], expected: bool):
    
    id = "Metadata/Items/" + id_suffix
    base_info = _create_info(**info)

    result = base_validation.validate(id, base_info)

    assert result == expected

def test_validate_given_unrecognized_base_id_structure_should_raise():
    INCORRECT_BASE_ID = "incorrect_base_id"

    with pytest.raises(ValueError) as error:
        _ = base_validation.validate(INCORRECT_BASE_ID, {})

    assert str(error.value) == _UNRECOGNIZED_BASE_ID_ERROR.format(INCORRECT_BASE_ID)

def _create_info(
    name: str = _BASE_NAME,
    release_state: _ReleaseState = _ReleaseState.RELEASED):
    return { Field.NAME: name, Field.RELEASE_STATE: release_state }