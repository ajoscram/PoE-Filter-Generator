import pytest, ggg, ninja
from pytest import MonkeyPatch
from handlers import econ
from core import ExpectedError, COMMENT_START, EQUALS, REPLICA, RULE_START, BASE_TYPE as BASE_TYPES_OPERAND
from handlers.econ import _QUERY_TYPES_BY_MNEMONIC, _LOWER_BOUND_NAME, _RULE_BOUNDS_ERROR, _RULE_MNEMONIC_ERROR, _UPPER_BOUND_NAME, NAME as ECON, _RULE_PARAMETER_COUNT_ERROR
from test_utilities import FunctionMock, create_filter

_LEAGUE_NAME = "league_name"
_NON_INT = "non_int"
_MNEMONIC = list(_QUERY_TYPES_BY_MNEMONIC.keys())[0]
# _LOWER_BOUND = 1
# _UPPER_BOUND = 3
# _BASE_TYPES = [ "base_type_1", "base_type_2" ]

@pytest.fixture(autouse=True)
def get_league_name_mock(monkeypatch: MonkeyPatch):
    return FunctionMock(monkeypatch, ggg.get_league_name, _LEAGUE_NAME)

@pytest.mark.parametrize("param_count", [1, 4])
def test_handle_given_incorrect_rule_params_count_should_raise(param_count: int):
    PARAMS = [ str(i) for i in range(param_count) ]
    FILTER = create_filter(f"{RULE_START}{ECON} {' '.join(PARAMS)}")

    with pytest.raises(ExpectedError) as error:
        _ = econ.handle(FILTER, FILTER.blocks[0], [])
    
    assert error.value.message == _RULE_PARAMETER_COUNT_ERROR.format(param_count)
    assert error.value.line_number == FILTER.blocks[0].lines[0].number

def test_handle_given_unknown_mnemonic_should_raise():
    UNKNOWN_MNEMONIC = "unknown_mnemonic"
    FILTER = create_filter(f"{RULE_START}{ECON} {UNKNOWN_MNEMONIC} 1")

    with pytest.raises(ExpectedError) as error:
        _ = econ.handle(FILTER, FILTER.blocks[0], [])
    
    assert error.value.message == _RULE_MNEMONIC_ERROR.format(UNKNOWN_MNEMONIC)
    assert error.value.line_number == FILTER.blocks[0].lines[0].number

@pytest.mark.parametrize("param_1, param_2, bound_name", [
    (_NON_INT, "1", _LOWER_BOUND_NAME),
    ("1", _NON_INT, _UPPER_BOUND_NAME)
])
def test_handle_given_non_int_rule_params_should_raise(param_1: str, param_2: str, bound_name: str):
    FILTER = create_filter(f"{RULE_START}{ECON} {_MNEMONIC} {param_1} {param_2}")

    with pytest.raises(ExpectedError) as error:
        _ = econ.handle(FILTER, FILTER.blocks[0], [])

    assert error.value.message == _RULE_BOUNDS_ERROR.format(bound_name, _NON_INT)
    assert error.value.line_number == FILTER.blocks[0].lines[0].number

def test_handle_given_no_base_types_are_found_should_comment_out_the_block(monkeypatch: MonkeyPatch):
    FILTER = create_filter(f"{REPLICA} {EQUALS} True {RULE_START}{ECON} {_MNEMONIC} 1")
    _ = FunctionMock(monkeypatch, ninja.get_bases, set())

    lines = econ.handle(FILTER, FILTER.blocks[0], [])

    assert lines[0].startswith(COMMENT_START)

def test_given_a_valid_mnemonic_should_set_the_base_types_to_the_block(monkeypatch: MonkeyPatch):
    LOWER_BOUND = 1
    UPPER_BOUND = 4
    BASE_TYPES = { "base 1", "base 2" }
    EXPECTED_QUERY_TYPE = list(_QUERY_TYPES_BY_MNEMONIC[_MNEMONIC])[0]
    FILTER = create_filter(f"{BASE_TYPES_OPERAND} {RULE_START}{ECON} {_MNEMONIC} {LOWER_BOUND} {UPPER_BOUND}")
    ninja_mock = FunctionMock(monkeypatch, ninja.get_bases, BASE_TYPES)

    lines = econ.handle(FILTER, FILTER.blocks[0], [])

    assert ninja_mock.received(_LEAGUE_NAME, EXPECTED_QUERY_TYPE, LOWER_BOUND, UPPER_BOUND)
    for base_type in BASE_TYPES:
        assert f'"{base_type}"' in lines[0]