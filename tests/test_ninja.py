from dataclasses import dataclass
import pytest, ninja, repoe
from pytest import MonkeyPatch
from ninja import ValueRange
from ninja.constants import *
from test_utilities import FunctionMock, WebGetMock, create_sieve_for_text, create_sieve_for_pattern
from ninja.utils import _REPLICA_ITEM_NAME_EXCEPTIONS
from core import Operand

_LEAGUE_NAME = "league_name"
_ITEM_CLASS = "item class"
_BASE_TYPE = "base type"
_CLUSTER_ENCHANT = "cluster enchant"
_CLUSTER_STAT_TEXT = "cluster stat text"
_RANGE = ValueRange(1, 2)
_VALUE_IN_RANGE = _RANGE.upper - _RANGE.lower
_DEFAULT_SIEVE = create_sieve_for_text("Show")

@dataclass
class _DefaultExchangeResponse:
    value: int

    def __call__(self, *_, **__):
        record = { Field.ID: Field.ID, Field.PRIMARY_VALUE: self.value }
        item = { Field.ID: Field.ID, Field.NAME: _BASE_TYPE }
        return { Field.LINES: [ record ], Field.ITEMS: [ item ] }

@dataclass
class _UniqueResponse:
    name: str = "name"
    class_: str = _ITEM_CLASS
    links: int = 0
    
    def __call__(self, *_, **__):
        record = {
            Field.BASE_TYPE: _BASE_TYPE,
            Field.CHAOS_VALUE: _VALUE_IN_RANGE,
            Field.NAME: self.name,
            Field.CLASS: self.class_,
            Field.LINKS: self.links,
        }

        return { Field.LINES: [ record ] }

@dataclass
class _GemResponse:
    level: int = 1
    quality: int = 0
    corrupted: bool = False

    def __call__(self, *_, **__):
        record = {
            Field.NAME: _BASE_TYPE,
            Field.CHAOS_VALUE: _VALUE_IN_RANGE,
            Field.GEM_LEVEL: self.level,
            Field.GEM_QUALITY: self.quality,
            Field.CORRUPTED: self.corrupted,
        }

        return { Field.LINES: [ record ] }

@dataclass
class _WombgiftResponse:
    level: int = 1

    def __call__(self, *_, **__):
        record = {
            Field.NAME: _BASE_TYPE,
            Field.CHAOS_VALUE: _VALUE_IN_RANGE,
            Field.LEVEL_REQUIRED: self.level,
        }

        return { Field.LINES: [ record ] }

@dataclass
class _ClusterJewelResponse:
    base_type: str = _BASE_TYPE
    passives: int = 1
    level: int = 1

    def __call__(self, *_, **__):
        record = {
            Field.NAME: _CLUSTER_STAT_TEXT,
            Field.BASE_TYPE: self.base_type,
            Field.LEVEL_REQUIRED: self.level,
            Field.CHAOS_VALUE: _VALUE_IN_RANGE,
            Field.VARIANT: f"{self.passives} passives",
        }

        return { Field.LINES: [ record ] }

@pytest.fixture(autouse=True)
def get_class_for_base_mock(monkeypatch: MonkeyPatch):
    return FunctionMock(monkeypatch, repoe.get_class_for_base, _ITEM_CLASS)

@pytest.fixture(autouse=True)
def get_cluster_enchan_mock(monkeypatch: MonkeyPatch):
    return FunctionMock(monkeypatch, repoe.get_cluster_enchant, _CLUSTER_ENCHANT)

@pytest.fixture(autouse=True)
def web_get_mock(monkeypatch: MonkeyPatch):
    return WebGetMock(monkeypatch, NotImplementedError)

@pytest.mark.parametrize("value, is_in_range", [
    (_VALUE_IN_RANGE, True),
    (_RANGE.upper + 1, False),
])
def test_get_base_types_given_a_range_should_return_if_in_it(
    web_get_mock: WebGetMock, value: int, is_in_range: bool):

    QUERY_TYPE = BaseQueryType.CURRENCY # chosen arbitrarily
    web_get_mock.result = _DefaultExchangeResponse(value)

    base_types = ninja.get_base_types(QUERY_TYPE, _LEAGUE_NAME, _DEFAULT_SIEVE, _RANGE)

    assert (_BASE_TYPE in base_types) == is_in_range

@pytest.mark.parametrize("foulborn", [ True, False ])
def test_get_base_types_given_foulborn_unique_should_return_depending_on_sieve(
    web_get_mock: WebGetMock, foulborn: bool):

    NAME = f"{Operand.FOULBORN} {_BASE_TYPE}"
    SIEVE = create_sieve_for_pattern({ Operand.FOULBORN: foulborn })
    web_get_mock.result = _UniqueResponse(name=NAME)
    
    base_types = ninja.get_base_types(BaseQueryType.UNIQUE_ARMOUR, _LEAGUE_NAME, SIEVE, _RANGE)

    assert (_BASE_TYPE in base_types) == foulborn

@pytest.mark.parametrize("replica", [ True, False ])
def test_get_base_types_given_replica_unique_should_return_depending_on_sieve(
    web_get_mock: WebGetMock, replica: bool):

    NAME = f"{Operand.REPLICA} {_BASE_TYPE}"
    SIEVE = create_sieve_for_pattern({ Operand.REPLICA: replica })
    web_get_mock.result = _UniqueResponse(name=NAME)
    
    base_types = ninja.get_base_types(BaseQueryType.UNIQUE_ARMOUR, _LEAGUE_NAME, SIEVE, _RANGE)

    assert (_BASE_TYPE in base_types) == replica

@pytest.mark.parametrize("replica", [ True, False ])
def test_get_base_types_given_replica_unique_name_exceptions_should_return_depending_on_sieve(
    web_get_mock: WebGetMock, replica: bool):

    SIEVE = create_sieve_for_pattern({ Operand.REPLICA: replica })
    web_get_mock.result = _UniqueResponse(name=_REPLICA_ITEM_NAME_EXCEPTIONS[0])

    base_types = ninja.get_base_types(BaseQueryType.UNIQUE_ACCESSORY, _LEAGUE_NAME, SIEVE, _RANGE)

    assert (_BASE_TYPE in base_types) != replica

@pytest.mark.parametrize("links", [ 3, 4 ])
def test_get_base_types_given_unique_with_links_should_return_depending_on_sieve(
    web_get_mock: WebGetMock, links: int):

    SIEVE = create_sieve_for_pattern({ Operand.LINKED_SOCKETS: links })
    web_get_mock.result = _UniqueResponse(links=3)

    base_types = ninja.get_base_types(BaseQueryType.UNIQUE_WEAPON, _LEAGUE_NAME, SIEVE, _RANGE)
    
    assert (_BASE_TYPE in base_types) == (links == web_get_mock.result.links)

@pytest.mark.parametrize("class_", [ _ITEM_CLASS, "another class" ])
def test_get_base_types_given_unique_with_class_should_return_depending_on_sieve(
    web_get_mock: WebGetMock, class_: str):
    
    SIEVE = create_sieve_for_pattern({ Operand.CLASS: f'"{class_}"' })
    web_get_mock.result = _UniqueResponse(class_=_ITEM_CLASS)

    base_types = ninja.get_base_types(BaseQueryType.UNIQUE_JEWEL, _LEAGUE_NAME, SIEVE, _RANGE)

    assert (_BASE_TYPE in base_types) == (class_ == _ITEM_CLASS)

@pytest.mark.parametrize("level", [ 1, 2 ])
def test_get_base_types_given_gem_with_level_should_return_depending_on_sieve(
    web_get_mock: WebGetMock, level: bool):
    
    SIEVE = create_sieve_for_pattern({ Operand.GEM_LEVEL: level })
    web_get_mock.result = _GemResponse(level=1)

    base_types = ninja.get_base_types(BaseQueryType.GEM, _LEAGUE_NAME, SIEVE, _RANGE)

    assert (_BASE_TYPE in base_types) == (level == web_get_mock.result.level)

@pytest.mark.parametrize("quality", [ 0, 1 ])
def test_get_base_types_given_gem_with_quality_should_return_depending_on_sieve(
    web_get_mock: WebGetMock, quality: bool):
    
    SIEVE = create_sieve_for_pattern({ Operand.QUALITY: quality })
    web_get_mock.result = _GemResponse(quality=0)

    base_types = ninja.get_base_types(BaseQueryType.GEM, _LEAGUE_NAME, SIEVE, _RANGE)

    assert (_BASE_TYPE in base_types) == (quality == web_get_mock.result.quality)

@pytest.mark.parametrize("corrupted", [ True, False ])
def test_get_base_types_given_corrupted_gem_should_return_depending_on_sieve(
    web_get_mock: WebGetMock, corrupted: bool):

    SIEVE = create_sieve_for_pattern({ Operand.CORRUPTED: corrupted })
    web_get_mock.result = _GemResponse(corrupted=True)

    base_types = ninja.get_base_types(BaseQueryType.GEM, _LEAGUE_NAME, SIEVE, _RANGE)

    assert (_BASE_TYPE in base_types) == corrupted

@pytest.mark.parametrize("base_type", [ _BASE_TYPE, "unknown base" ])
def test_get_cluster_enchants_given_base_type_should_return_depending_on_sieve(
    web_get_mock: WebGetMock, base_type: str):
    
    SIEVE = create_sieve_for_pattern({ Operand.BASE_TYPE: f"\"{base_type}\"" })
    web_get_mock.result = _ClusterJewelResponse(base_type=_BASE_TYPE)

    enchants = ninja.get_cluster_enchants(_LEAGUE_NAME, SIEVE, _RANGE)

    assert (_CLUSTER_ENCHANT in enchants) == (base_type == web_get_mock.result.base_type)

@pytest.mark.parametrize("base_type", [ _BASE_TYPE, "unknown base" ])
def test_get_cluster_enchants_given_base_type_should_return_depending_on_sieve(
    web_get_mock: WebGetMock, base_type: str):
    
    SIEVE = create_sieve_for_pattern({ Operand.BASE_TYPE: f"\"{base_type}\"" })
    web_get_mock.result = _ClusterJewelResponse(base_type=_BASE_TYPE)

    enchants = ninja.get_cluster_enchants(_LEAGUE_NAME, SIEVE, _RANGE)

    assert (_CLUSTER_ENCHANT in enchants) == (base_type == web_get_mock.result.base_type)

@pytest.mark.parametrize("level", [ 1, 2 ])
def test_get_cluster_enchants_given_level_should_return_depending_on_sieve(
    web_get_mock: WebGetMock, level: int):
    
    SIEVE = create_sieve_for_pattern({ Operand.ITEM_LEVEL: level })
    web_get_mock.result = _ClusterJewelResponse(level=1)

    enchants = ninja.get_cluster_enchants(_LEAGUE_NAME, SIEVE, _RANGE)

    assert (_CLUSTER_ENCHANT in enchants) == (level == web_get_mock.result.level)

@pytest.mark.parametrize("passives", [ 1, 2 ])
def test_get_cluster_enchants_given_enchantment_pasive_number_should_return_depending_on_sieve(
    web_get_mock: WebGetMock, passives: int):
    
    SIEVE = create_sieve_for_pattern({ Operand.ENCHANTMENT_PASSIVE_NUM: passives })
    web_get_mock.result = _ClusterJewelResponse(passives=1)

    enchants = ninja.get_cluster_enchants(_LEAGUE_NAME, SIEVE, _RANGE)

    assert (_CLUSTER_ENCHANT in enchants) == (passives == web_get_mock.result.level)

@pytest.mark.parametrize("level", [ 0, 1 ])
def test_get_base_types_given_item_level_for_wombgift_should_return_depending_on_sieve(
    web_get_mock: WebGetMock, level: int):
    
    SIEVE = create_sieve_for_pattern({ Operand.ITEM_LEVEL: level })
    web_get_mock.result = _WombgiftResponse(level=0)

    base_types = ninja.get_base_types(BaseQueryType.WOMBGIFT, _LEAGUE_NAME, SIEVE, _RANGE)

    assert (_BASE_TYPE in base_types) == (level == web_get_mock.result.level)