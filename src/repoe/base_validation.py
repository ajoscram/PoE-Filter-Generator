from enum import StrEnum
from . import gem
from .constants import Field, ROYALE_PATTERN
from .matchable import Matchable

class _BaseTypeName(StrEnum):
    BLADE_TRAP = "Blade Trap"
    ENERGY_BLADE = "Energy Blade"
    ORNATE_QUIVER = "Ornate Quiver"

class _ReleaseState(StrEnum):
    LEGACY = "legacy"
    RELEASED = "released"
    UNIQUE_ONLY = "unique_only"
    UNRELEASED = "unreleased"

class _IDPrefixPattern(StrEnum):
    MISC = r"Metadata/Items/[^/]+/(.+)"
    MAP = r"Metadata/Items/Maps/(.+)"
    GEM = r"Metadata/Items/Gems/(.+)"
    DELVE = r"Metadata/Items/Delve/(.+)"
    RELIC = r"Metadata/Items/Relics/(.+)"
    QUIVER = r"Metadata/Items/Quivers/(.+)"
    WEAPON = r"Metadata/Items/Weapons/(.+)"
    CURRENCY = r"Metadata/Items/Currency/(.+)"
    MAP_FRAGMENT = r"Metadata/Items/MapFragments/(.+)"
    TALISMAN = r"Metadata/Items/Amulets/Talismans/(.+)"
    ATLAS_UPGRADE = r"Metadata/Items/AtlasUpgrades/(.+)"
    MTX_CURRENCY = r"Metadata/Items/MicrotransactionCurrency/(.+)"

class _IDSuffixPattern(StrEnum):
    VOIDSTONE = r"\w+Primordial\d"
    MAVEN_INVITATION = r"Maven/(.+)"
    CURRENT_SERIES_MAP = r"MapWorlds.+"
    HARBINGER_MAP_DUPE = r".+Harbinger(?:Mid|High|Uber)"
    MAVEN_ATLAS_INVITATION = r".+Atlas1"
    RELIC_DUPE = r"^Relic\dx\d"
    QUIVER_DUPE = r"Quiver(?:Descent|\d+)"
    TALISMAN_DUPE = r"Talisman\d+_\d+_[^1]"
    FOSSIL_OUTCOME = r"RandomFossilOutcome\d+"
    SILVER_COIN_DUPE = r"CurrencySilverCoin"
    DIVINE_VESSEL_DUPE = r"FragmentPantheonFlask"
    INCURSION_CORRUPT = r"CurrencyIncursionCorrupt.+"
    TENCENT_VOIDBORN_KEY = r"TencentVoidbornVaultKey"
    FRAGMENT_DUPE = r"^(?:Vaal|Prophecy|Shaper)Fragment[\d_]+"
    DELVE_STACKABLE_RESONATOR = r"DelveStackableSocketableCurrency.+"
    DELIRIUM_ORB_DUPE = r"CurrencyAfflictionOrb(?:Prophecies|Generic)"

_INVALID_CURRENCY_PATTERNS = [
    _IDSuffixPattern.FOSSIL_OUTCOME, _IDSuffixPattern.INCURSION_CORRUPT, \
    _IDSuffixPattern.SILVER_COIN_DUPE, _IDSuffixPattern.DELIRIUM_ORB_DUPE ]
_INVALID_FRAGMENT_PATTERNS = [
    _IDSuffixPattern.FRAGMENT_DUPE, _IDSuffixPattern.DIVINE_VESSEL_DUPE, \
    _IDSuffixPattern.TENCENT_VOIDBORN_KEY ]

_UNRECOGNIZED_BASE_ID_ERROR = "Unrecognized base_id: {0}"

def validate(base_id: str, base_info: dict[str]) -> bool:
    """Returns `True` if `base_id` and `base_info` correspond to a valid base type. `False` otherwise."""
    match Matchable(base_id):
        case _IDPrefixPattern.MTX_CURRENCY:
            return False
        case _IDPrefixPattern.CURRENCY as match:
            return _is_currency_valid(match[1])
        case _IDPrefixPattern.DELVE as match:
            return _is_resonator_valid(match[1])
        case _IDPrefixPattern.MAP as match:
            return _is_map_valid(match[1])
        case _IDPrefixPattern.GEM as match:
            return _is_gem_valid(match[0], match[1], base_info)
        case _IDPrefixPattern.TALISMAN as match:
            return _is_talisman_valid(match[1])
        case _IDPrefixPattern.ATLAS_UPGRADE as match:
            return _is_atlas_upgrade_valid(match[1])
        case _IDPrefixPattern.MAP_FRAGMENT as match:
            return _is_map_fragment_valid(match[1])
        case _IDPrefixPattern.WEAPON as match:
            return _is_weapon_valid(match[1], base_info)
        case _IDPrefixPattern.QUIVER as match:
            return _is_quiver_valid(match[1], base_info)
        case _IDPrefixPattern.RELIC as match:
            return _is_relic_valid(match[1])
        case _IDPrefixPattern.MISC as match:
            return _is_misc_valid(match[1], base_info)
        case _:
            raise ValueError(_UNRECOGNIZED_BASE_ID_ERROR.format(base_id))

def _is_currency_valid(id: str):
    return Matchable(id) not in _INVALID_CURRENCY_PATTERNS

def _is_map_fragment_valid(id: str):
    match Matchable(id):
        case x if x in _INVALID_FRAGMENT_PATTERNS:
            return False
        case _IDSuffixPattern.MAVEN_INVITATION as match:
            return Matchable(match[1]) == _IDSuffixPattern.MAVEN_ATLAS_INVITATION
        case _:
            return True

def _is_map_valid(id: str):
    match Matchable(id):
        case _IDSuffixPattern.HARBINGER_MAP_DUPE:
            return False
        case _IDSuffixPattern.CURRENT_SERIES_MAP:
            return True
        case _:
            return False

def _is_gem_valid(full_id: str, id: str, info: dict[str]):
    if Matchable(id) == ROYALE_PATTERN or not gem.is_base_gem(full_id):
        return False

    unreleased = info[Field.RELEASE_STATE] == _ReleaseState.UNRELEASED
    is_blade_trap = info[Field.NAME] == _BaseTypeName.BLADE_TRAP
    return not unreleased or is_blade_trap

def _is_resonator_valid(id: str):
    return Matchable(id) == _IDSuffixPattern.DELVE_STACKABLE_RESONATOR

def _is_talisman_valid(id: str):
    return Matchable(id) != _IDSuffixPattern.TALISMAN_DUPE

def _is_atlas_upgrade_valid(id: str):
    return Matchable(id) == _IDSuffixPattern.VOIDSTONE

def _is_weapon_valid(id: str, info: dict[str]):
    is_energy_blade = info[Field.NAME] == _BaseTypeName.ENERGY_BLADE
    return not is_energy_blade and _is_misc_valid(id, info)

def _is_relic_valid(id: str):
    return Matchable(id) != _IDSuffixPattern.RELIC_DUPE

def _is_quiver_valid(id: str, info: dict[str]):
    dupe = Matchable(id) == _IDSuffixPattern.QUIVER_DUPE
    is_ornate = info[Field.NAME] == _BaseTypeName.ORNATE_QUIVER
    return (not dupe or is_ornate) and _is_misc_valid(id, info)

def _is_misc_valid(id: str, info: dict[str]):
    royale = Matchable(id) == ROYALE_PATTERN
    unreleased = info[Field.RELEASE_STATE] == _ReleaseState.UNRELEASED
    return not unreleased and not royale