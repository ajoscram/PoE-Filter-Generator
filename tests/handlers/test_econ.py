import pytest, ggg, ninja
from pytest import MonkeyPatch
from handlers import econ
from core import ExpectedError, COMMENT_START, EQUALS, REPLICA, RULE_START, BASE_TYPE as BASE_TYPES_OPERAND
from handlers.econ import _CURRENCY_MNEMONICS, _LOWER_BOUND_NAME, _MISC_MNEMONICS, _RULE_BOUNDS_ERROR, _RULE_MNEMONIC_ERROR, _UNIQUE_MNEMONIC, _UPPER_BOUND_NAME, NAME as ECON, _RULE_PARAMETER_COUNT_ERROR
from test_utilities import FunctionMock, create_filter

_LEAGUE_NAME = "league_name"
_NON_INT = "non_int"
_LOWER_BOUND = 1
_UPPER_BOUND = 3
_BASE_TYPES = [ "base_type_1", "base_type_2" ]

@pytest.fixture(autouse=True)
def setup(monkeypatch: MonkeyPatch):
    _ = FunctionMock(monkeypatch, ggg.get_league_name, _LEAGUE_NAME)

@pytest.mark.parametrize("param_count", [1, 4])
def test_handle_given_incorrect_rule_params_count_should_raise(param_count: int):
    PARAMS = [ str(i) for i in range(param_count) ]
    FILTER = create_filter(f"{RULE_START}{ECON} {' '.join(PARAMS)}")

    with pytest.raises(ExpectedError) as error:
        _ = econ.handle(FILTER, FILTER.blocks[0], [])
    
    assert error.value.message == _RULE_PARAMETER_COUNT_ERROR.format(param_count)
    assert error.value.line_number == FILTER.blocks[0].lines[0].number

@pytest.mark.parametrize("int_param_1, int_param_2, bound_name", [
    (_NON_INT, "1", _LOWER_BOUND_NAME),
    ("1", _NON_INT, _UPPER_BOUND_NAME)
])
def test_handle_given_non_int_rule_params_should_raise(int_param_1: str, int_param_2: str, bound_name: str):
    FILTER = create_filter(f"{RULE_START}{ECON} nmemonic {int_param_1} {int_param_2}")

    with pytest.raises(ExpectedError) as error:
        _ = econ.handle(FILTER, FILTER.blocks[0], [])
    
    assert error.value.message == _RULE_BOUNDS_ERROR.format(bound_name, _NON_INT)
    assert error.value.line_number == FILTER.blocks[0].lines[0].number

def test_handle_given_unknown_mnemonic_should_raise():
    UNKNOWN_MNEMONIC = "unknown_mnemonic"
    FILTER = create_filter(f"{RULE_START}{ECON} {UNKNOWN_MNEMONIC} 1")

    with pytest.raises(ExpectedError) as error:
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
    FILTER = create_filter(f"{BASE_TYPES_OPERAND} {RULE_START}{ECON} {MNEMONIC} {_LOWER_BOUND} {_UPPER_BOUND}")
    ninja_mock = FunctionMock(monkeypatch, ninja.get_currency_base_types, _BASE_TYPES)

    lines = econ.handle(FILTER, FILTER.blocks[0], [])

    assert ninja_mock.received(_LEAGUE_NAME, _CURRENCY_MNEMONICS[MNEMONIC], _LOWER_BOUND, _UPPER_BOUND)
    for base_type in _BASE_TYPES:
        assert f'"{base_type}"' in lines[0]
    
def test_given_a_misc_mnemonic_should_set_the_base_types_to_the_block(monkeypatch: MonkeyPatch):
    MNEMONIC = list(_MISC_MNEMONICS.keys())[0]
    FILTER = create_filter(f"{BASE_TYPES_OPERAND} {RULE_START}{ECON} {MNEMONIC} {_LOWER_BOUND} {_UPPER_BOUND}")
    ninja_mock = FunctionMock(monkeypatch, ninja.get_misc_base_types, _BASE_TYPES)

    lines = econ.handle(FILTER, FILTER.blocks[0], [])

    assert ninja_mock.received(_LEAGUE_NAME, _MISC_MNEMONICS[MNEMONIC], _LOWER_BOUND, _UPPER_BOUND)
    for base_type in _BASE_TYPES:
        assert f'"{base_type}"' in lines[0]

def test_given_a_unique_rule_should_set_the_base_types_to_the_block(monkeypatch: MonkeyPatch):
    FILTER = create_filter(f"{BASE_TYPES_OPERAND} {RULE_START}{ECON} {_UNIQUE_MNEMONIC} {_LOWER_BOUND} {_UPPER_BOUND}")
    ninja_mock = FunctionMock(monkeypatch, ninja.get_unique_base_types, _BASE_TYPES)

    lines = econ.handle(FILTER, FILTER.blocks[0], [])

    assert ninja_mock.received(_LEAGUE_NAME, _LOWER_BOUND, _UPPER_BOUND)
    for base_type in _BASE_TYPES:
        assert f'"{base_type}"' in lines[0]