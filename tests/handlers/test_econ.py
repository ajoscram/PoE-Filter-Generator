import pytest, ggg, ninja, utils
from ninja import UniqueFilter
from core import GeneratorError
from pytest import MonkeyPatch
from handlers import econ
from handlers.econ import _CURRENCY_MNEMONICS, _LOWER_BOUND_NAME, _MISC_MNEMONICS, _RULE_BOUNDS_ERROR, _RULE_MNEMONIC_ERROR, _UNIQUE_MNEMONIC, _UPPER_BOUND_NAME, NAME as ECON, _RULE_PARAMETER_COUNT_ERROR
from core.constants import CLASS, COMMENT_START, CONTAINS, EQUALS, GREATER, GREATER_EQUALS, LESS, LESS_EQUALS, LINKED_SOCKETS, REPLICA, RULE_START, BASE_TYPE as BASE_TYPES_OPERAND
from tests.test_utilities import FunctionMock, create_filter

LEAGUE_NAME = "league_name"
NON_INT = "non_int"
LOWER_BOUND = 1
UPPER_BOUND = 3
SOCKET_LINKS = 4
BASE_TYPES = [ "base_type_1", "base_type_2" ]

@pytest.fixture(autouse=True)
def setup(monkeypatch: MonkeyPatch):
    _ = FunctionMock(monkeypatch, ggg.get_league_name, LEAGUE_NAME)
    _ = FunctionMock(monkeypatch, utils.try_translate_class, lambda x: x)

@pytest.mark.parametrize("param_count", [1, 4])
def test_handle_given_incorrect_rule_params_count_should_raise(param_count: int):
    PARAMS = [ str(i) for i in range(param_count) ]
    FILTER = create_filter(f"{RULE_START}{ECON} {' '.join(PARAMS)}")

    with pytest.raises(GeneratorError) as error:
        _ = econ.handle(FILTER, FILTER.blocks[0], [])
    
    assert error.value.message == _RULE_PARAMETER_COUNT_ERROR.format(param_count)
    assert error.value.line_number == FILTER.blocks[0].lines[0].number

@pytest.mark.parametrize("int_param_1, int_param_2, bound_name", [
    (NON_INT, "1", _LOWER_BOUND_NAME),
    ("1", NON_INT, _UPPER_BOUND_NAME)
])
def test_handle_given_non_int_rule_params_should_raise(int_param_1: str, int_param_2: str, bound_name: str):
    FILTER = create_filter(f"{RULE_START}{ECON} nmemonic {int_param_1} {int_param_2}")

    with pytest.raises(GeneratorError) as error:
        _ = econ.handle(FILTER, FILTER.blocks[0], [])
    
    assert error.value.message == _RULE_BOUNDS_ERROR.format(bound_name, NON_INT)
    assert error.value.line_number == FILTER.blocks[0].lines[0].number

def test_handle_given_unknown_mnemonic_should_raise():
    UNKNOWN_MNEMONIC = "unknown_mnemonic"
    FILTER = create_filter(f"{RULE_START}{ECON} {UNKNOWN_MNEMONIC} 1")

    with pytest.raises(GeneratorError) as error:
        _ = econ.handle(FILTER, FILTER.blocks[0], [])
    
    assert error.value.message == _RULE_MNEMONIC_ERROR.format(UNKNOWN_MNEMONIC)
    assert error.value.line_number == FILTER.blocks[0].lines[0].number

def test_handle_given_no_base_types_are_found_should_comment_out_the_block(monkeypatch: MonkeyPatch):
    EMPTY_BASE_TYPES = []
    FILTER = create_filter(f"{REPLICA} {EQUALS} True {RULE_START}{ECON} {_UNIQUE_MNEMONIC} 1")
    _ = FunctionMock(monkeypatch, ninja.get_unique_base_types, EMPTY_BASE_TYPES)

    lines = econ.handle(FILTER, FILTER.blocks[0], [])

    assert lines[0].startswith(COMMENT_START)


def test_given_a_currency_mnemonic_should_set_the_base_types_to_the_block(monkeypatch: MonkeyPatch):
    MNEMONIC = list(_CURRENCY_MNEMONICS.keys())[0]
    FILTER = create_filter(f"{BASE_TYPES_OPERAND} {RULE_START}{ECON} {MNEMONIC} {LOWER_BOUND} {UPPER_BOUND}")
    ninja_mock = FunctionMock(monkeypatch, ninja.get_currency_base_types, BASE_TYPES)

    lines = econ.handle(FILTER, FILTER.blocks[0], [])

    assert ninja_mock.received(LEAGUE_NAME, _CURRENCY_MNEMONICS[MNEMONIC], LOWER_BOUND, UPPER_BOUND)
    for base_type in BASE_TYPES:
        assert f'"{base_type}"' in lines[0]
    
def test_given_a_misc_mnemonic_should_set_the_base_types_to_the_block(monkeypatch: MonkeyPatch):
    MNEMONIC = list(_MISC_MNEMONICS.keys())[0]
    FILTER = create_filter(f"{BASE_TYPES_OPERAND} {RULE_START}{ECON} {MNEMONIC} {LOWER_BOUND} {UPPER_BOUND}")
    ninja_mock = FunctionMock(monkeypatch, ninja.get_misc_base_types, BASE_TYPES)

    lines = econ.handle(FILTER, FILTER.blocks[0], [])

    assert ninja_mock.received(LEAGUE_NAME, _MISC_MNEMONICS[MNEMONIC], LOWER_BOUND, UPPER_BOUND)
    for base_type in BASE_TYPES:
        assert f'"{base_type}"' in lines[0]

def test_given_a_unique_rule_should_set_the_base_types_to_the_block(monkeypatch: MonkeyPatch):
    FILTER = create_filter(f"{BASE_TYPES_OPERAND} {RULE_START}{ECON} {_UNIQUE_MNEMONIC} {LOWER_BOUND} {UPPER_BOUND}")
    ninja_mock = FunctionMock(monkeypatch, ninja.get_unique_base_types, BASE_TYPES)

    lines = econ.handle(FILTER, FILTER.blocks[0], [])

    assert ninja_mock.received(LEAGUE_NAME, LOWER_BOUND, UPPER_BOUND)
    for base_type in BASE_TYPES:
        assert f'"{base_type}"' in lines[0]

def test_given_a_unique_rule_with_classes_should_filter_for_classes(monkeypatch: MonkeyPatch):
    CLASSES = [ "class_1", "class_2" ]
    FILTER = create_filter(
    f"""{BASE_TYPES_OPERAND} {RULE_START}{ECON} {_UNIQUE_MNEMONIC} {LOWER_BOUND}
        {CLASS} == {' '.join(CLASSES)}""")
    ninja_mock = FunctionMock(monkeypatch, ninja.get_unique_base_types, BASE_TYPES)

    _ = econ.handle(FILTER, FILTER.blocks[0], [])

    unique_filter: UniqueFilter = ninja_mock.get_arg(UniqueFilter)
    assert unique_filter.classes == CLASSES
    
@pytest.mark.parametrize("replica", [True, False])
def test_given_a_unique_rule_with_replica_should_filter_for_replicas(monkeypatch: MonkeyPatch, replica: bool):
    FILTER = create_filter(
    f"""{BASE_TYPES_OPERAND} {RULE_START}{ECON} {_UNIQUE_MNEMONIC} {LOWER_BOUND} {UPPER_BOUND}
        {REPLICA} == {replica}""")
    ninja_mock = FunctionMock(monkeypatch, ninja.get_unique_base_types, BASE_TYPES)

    _ = econ.handle(FILTER, FILTER.blocks[0], [])

    unique_filter: UniqueFilter = ninja_mock.get_arg(UniqueFilter)
    assert unique_filter.is_replica == replica

@pytest.mark.parametrize("operator, expected_min_links, expected_max_links", [
    (GREATER_EQUALS, SOCKET_LINKS, None),
    (GREATER, SOCKET_LINKS + 1, None),
    (LESS_EQUALS, None, SOCKET_LINKS),
    (LESS, None, SOCKET_LINKS - 1),
    ("", SOCKET_LINKS, SOCKET_LINKS),
    (CONTAINS, SOCKET_LINKS, SOCKET_LINKS),
    (EQUALS, SOCKET_LINKS, SOCKET_LINKS),
])
def test_given_a_unique_rule_with_links_should_filter_for_links(
    monkeypatch: MonkeyPatch, operator: str, expected_min_links: int, expected_max_links: int):
    FILTER = create_filter(
    f"""{BASE_TYPES_OPERAND} {RULE_START}{ECON} {_UNIQUE_MNEMONIC} {LOWER_BOUND} {UPPER_BOUND}
        {LINKED_SOCKETS} {operator} {SOCKET_LINKS}""")
    ninja_mock = FunctionMock(monkeypatch, ninja.get_unique_base_types, BASE_TYPES)

    _ = econ.handle(FILTER, FILTER.blocks[0], [])

    unique_filter: UniqueFilter = ninja_mock.get_arg(UniqueFilter)
    assert unique_filter.min_links == expected_min_links
    assert unique_filter.max_links == expected_max_links