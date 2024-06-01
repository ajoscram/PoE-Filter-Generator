from dataclasses import dataclass
import pytest, ninja, repoe
from pytest import MonkeyPatch
from ninja import ValueRange
from ninja.constants import *
from ninja.query import _MEMORY_SPLITTER, _UNKNOWN_GET_MODS_QUERY_TYPE
from test_utilities import FunctionMock, WebGetMock, create_sieve_for_text, create_sieve_for_pattern
from ninja.validation import _REPLICA_ITEM_NAME_EXCEPTIONS
from core import Operand

_LEAGUE_NAME = "league_name"
_VALUE = 5
_ITEM_CLASS = "item class"
_BASE_TYPE = "base type"
_DEFAULT_SIEVE = create_sieve_for_text("Show")
_RANGE = ValueRange(_VALUE)

@dataclass
class _Response:
    value: float = None
    base_type: str = None
    name: str = None
    links: int = None
    level_required: int = None
    corrupted: bool = None
    gem_level: int = None
    gem_quality: int = None
    
    def __call__(self, url: str, expiration, formatter):
        base_type_field = Field.CURRENCY_BASE_TYPE if "currency" in url else Field.ITEM_BASE_TYPE
        value_field = Field.CURRENCY_VALUE if "currency" in url else Field.ITEM_VALUE_FIELD
        record = {
            value_field: self.value or _VALUE,
            base_type_field: self.base_type or _BASE_TYPE,
            Field.NAME: self.name or _BASE_TYPE,
        }

        if self.links != None:
            record[Field.LINKS] = self.links
        
        if self.level_required != None:
            record[Field.LEVEL_REQUIRED] = self.level_required
        
        if self.corrupted != None:
            record[Field.CORRUPTED] = self.corrupted

        if self.gem_level != None:
            record[Field.GEM_LEVEL] = self.gem_level
        
        if self.gem_quality != None:
            record[Field.GEM_QUALITY] = self.gem_quality
        
        return { Field.LINES: [ record ] }

@pytest.fixture(autouse=True)
def get_class_for_base_mock(monkeypatch: MonkeyPatch):
    return FunctionMock(monkeypatch, repoe.get_class_for_base, _ITEM_CLASS)

@pytest.fixture(autouse=True)
def web_get_mock(monkeypatch: MonkeyPatch):
    return WebGetMock(monkeypatch, _Response())

@pytest.mark.parametrize("query_type", [ QueryType.CURRENCY, QueryType.ESSENCE ])
def test_get_bases_given_a_valid_record_was_found_should_return_it(query_type: QueryType):
    RANGE = ValueRange(_VALUE - 1, _VALUE + 1)

    base_types = ninja.get_bases(query_type, _LEAGUE_NAME, _DEFAULT_SIEVE, RANGE)

    assert _BASE_TYPE in base_types

@pytest.mark.parametrize("value", [ _VALUE - 1, _VALUE + 1 ])
def test_get_bases_given_outside_value_bounds_should_not_return_it(value: int, web_get_mock: WebGetMock):
    RANGE = ValueRange(_VALUE, _VALUE)
    web_get_mock.result = _Response(value=value)

    base_types = ninja.get_bases(QueryType.CURRENCY, _LEAGUE_NAME, _DEFAULT_SIEVE, RANGE)

    assert len(base_types) == 0

@pytest.mark.parametrize("item_level", [ 3, 4 ])
def test_get_bases_given_allflame_ember_should_return_depending_on_sieve(
    web_get_mock: WebGetMock, item_level: int):
    
    SIEVE_ITEM_LEVEL = 3
    SIEVE = create_sieve_for_pattern({ Operand.ITEM_LEVEL: SIEVE_ITEM_LEVEL })
    web_get_mock.result = _Response(level_required=item_level)

    base_types = ninja.get_bases(QueryType.ALLFLAME_EMBER, _LEAGUE_NAME, SIEVE, _RANGE)

    assert (_BASE_TYPE in base_types) == (item_level == SIEVE_ITEM_LEVEL)

@pytest.mark.parametrize("replica", [ True, False ])
def test_get_bases_given_replica_unique_base_should_return_depending_on_sieve(
    web_get_mock: WebGetMock, replica: bool):
    
    NAME = f"{Operand.REPLICA} {_BASE_TYPE}"
    SIEVE = create_sieve_for_pattern({ Operand.REPLICA: replica })
    web_get_mock.result = _Response(name=NAME)
    
    base_types = ninja.get_bases(QueryType.UNIQUE_ARMOUR, _LEAGUE_NAME, SIEVE, _RANGE)

    assert (_BASE_TYPE in base_types) == replica

@pytest.mark.parametrize("replica", [ True, False ])
def test_get_bases_given_replica_unique_name_exceptions_should_return_depending_on_sieve(
    web_get_mock: WebGetMock, replica: bool):

    SIEVE = create_sieve_for_pattern({ Operand.REPLICA: replica })
    web_get_mock.result = _Response(name=_REPLICA_ITEM_NAME_EXCEPTIONS[0])

    base_types = ninja.get_bases(QueryType.UNIQUE_ACCESSORY, _LEAGUE_NAME, SIEVE, _RANGE)

    assert (_BASE_TYPE in base_types) != replica

@pytest.mark.parametrize("links", [ 3, 4 ])
def test_get_bases_given_unique_with_links_should_return_depending_on_sieve(
    web_get_mock: WebGetMock, links: int):
    
    SIEVE_LINKS = 3
    SIEVE = create_sieve_for_pattern({ Operand.LINKED_SOCKETS: SIEVE_LINKS })
    web_get_mock.result = _Response(links=links)

    base_types = ninja.get_bases(QueryType.UNIQUE_WEAPON, _LEAGUE_NAME, SIEVE, _RANGE)
    
    assert (_BASE_TYPE in base_types) == (links == SIEVE_LINKS)

@pytest.mark.parametrize("class_", [ _ITEM_CLASS, "another class" ])
def test_get_bases_given_unique_with_class_should_return_depending_on_sieve(class_: str):
    SIEVE = create_sieve_for_pattern({ Operand.CLASS: f'"{class_}"' })

    base_types = ninja.get_bases(QueryType.UNIQUE_JEWEL, _LEAGUE_NAME, SIEVE, _RANGE)

    assert (_BASE_TYPE in base_types) == (class_ == _ITEM_CLASS)

@pytest.mark.parametrize("gem_level", [ _VALUE, _VALUE + 1 ])
def test_get_bases_given_gem_with_level_should_return_depending_on_sieve(web_get_mock: WebGetMock, gem_level: bool):
    SIEVE = create_sieve_for_pattern({ Operand.GEM_LEVEL: gem_level })
    web_get_mock.result = _Response(gem_level=_VALUE)

    base_types = ninja.get_bases(QueryType.GEM, _LEAGUE_NAME, SIEVE, _RANGE)

    assert (_BASE_TYPE in base_types) == (gem_level == web_get_mock.result.gem_level)

@pytest.mark.parametrize("gem_quality", [ _VALUE, _VALUE + 1 ])
def test_get_bases_given_gem_with_level_should_return_depending_on_sieve(web_get_mock: WebGetMock, gem_quality: bool):
    SIEVE = create_sieve_for_pattern({ Operand.QUALITY: gem_quality })
    web_get_mock.result = _Response(gem_level=1, gem_quality=_VALUE)

    base_types = ninja.get_bases(QueryType.GEM, _LEAGUE_NAME, SIEVE, _RANGE)

    assert (_BASE_TYPE in base_types) == (gem_quality == web_get_mock.result.gem_quality)

@pytest.mark.parametrize("corrupted", [ True, False ])
def test_get_bases_given_corrupted_gem_should_return_depending_on_sieve(web_get_mock: WebGetMock, corrupted: bool):
    SIEVE = create_sieve_for_pattern({ Operand.CORRUPTED: True })
    web_get_mock.result = _Response(gem_level=1, corrupted=corrupted)

    base_types = ninja.get_bases(QueryType.GEM, _LEAGUE_NAME, SIEVE, _RANGE)

    assert (_BASE_TYPE in base_types) == (corrupted == True)

def test_get_mods_given_memory_should_return_suffix_in_records_name(web_get_mock: WebGetMock):
    MOD = "of Suffixing"
    NAME = f"Master's {_MEMORY_SPLITTER}{MOD}"
    web_get_mock.result = _Response(name=NAME)

    mods = ninja.get_mods(QueryType.MEMORY, _LEAGUE_NAME, _DEFAULT_SIEVE, _RANGE)

    assert MOD in mods

def test_get_mods_given_invalid_query_type_should_raise():
    with pytest.raises(ValueError) as error:
        ninja.get_mods(QueryType.CURRENCY, _LEAGUE_NAME, _DEFAULT_SIEVE, _RANGE)

    assert str(error.value) == _UNKNOWN_GET_MODS_QUERY_TYPE.format(QueryType.CURRENCY)