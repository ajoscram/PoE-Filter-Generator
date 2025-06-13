import pytest, ggg, ninja
from handlers import econ, Context
from pytest import MonkeyPatch
from ninja import ValueRange, QueryType
from core import ExpectedError, Operator, Operand, Delimiter
from test_utilities import FunctionMock, create_filter
from handlers.econ import _QUERY_TYPES_BY_MNEMONIC, _LOWER_BOUND_NAME, _RULE_BOUNDS_ERROR, _RULE_MNEMONIC_ERROR, _UPPER_BOUND_NAME, NAME as ECON, _RULE_PARAMETER_COUNT_ERROR

_LEAGUE_NAME = "league_name"
_NON_INT = "non_int"
_QUERY_TYPE = QueryType.CURRENCY # chosen arbitrarily

@pytest.fixture(autouse=True)
def get_league_name_mock(monkeypatch: MonkeyPatch):
    return FunctionMock(monkeypatch, ggg.get_league_name, _LEAGUE_NAME)

@pytest.mark.parametrize("param_count", [1, 4])
def test_handle_given_incorrect_rule_params_count_should_raise(param_count: int):
    PARAMS = [ str(i) for i in range(param_count) ]
    FILTER = create_filter(f"{Delimiter.RULE_START}{ECON} {' '.join(PARAMS)}")

    with pytest.raises(ExpectedError) as error:
        _ = econ.handle(FILTER.blocks[0], Context(FILTER, []))
    
    assert error.value.message == _RULE_PARAMETER_COUNT_ERROR.format(param_count)
    assert error.value.line_number == FILTER.blocks[0].lines[0].number

def test_handle_given_unknown_mnemonic_should_raise():
    UNKNOWN_MNEMONIC = "unknown_mnemonic"
    FILTER = create_filter(f"{Delimiter.RULE_START}{ECON} {UNKNOWN_MNEMONIC} 1")

    with pytest.raises(ExpectedError) as error:
        _ = econ.handle(FILTER.blocks[0], Context(FILTER, []))
    
    assert error.value.message == _RULE_MNEMONIC_ERROR.format(UNKNOWN_MNEMONIC)
    assert error.value.line_number == FILTER.blocks[0].lines[0].number

@pytest.mark.parametrize("param_1, param_2, bound_name", [
    (_NON_INT, "1", _LOWER_BOUND_NAME),
    ("1", _NON_INT, _UPPER_BOUND_NAME)
])
def test_handle_given_non_int_rule_params_should_raise(param_1: str, param_2: str, bound_name: str):
    MNEMONIC = _get_mnemonic(_QUERY_TYPE)
    FILTER = create_filter(f"{Delimiter.RULE_START}{ECON} {MNEMONIC} {param_1} {param_2}")

    with pytest.raises(ExpectedError) as error:
        _ = econ.handle(FILTER.blocks[0], Context(FILTER, []))

    assert error.value.message == _RULE_BOUNDS_ERROR.format(bound_name, _NON_INT)
    assert error.value.line_number == FILTER.blocks[0].lines[0].number

def test_handle_given_no_base_types_are_found_should_comment_out_the_block(monkeypatch: MonkeyPatch):
    MNEMONIC = _get_mnemonic(_QUERY_TYPE)
    FILTER = create_filter(f"{Operand.REPLICA} {Operator.EQUALS} True {Delimiter.RULE_START}{ECON} {MNEMONIC} 1")
    _ = FunctionMock(monkeypatch, ninja.get_bases, set())

    lines = econ.handle(FILTER.blocks[0], Context(FILTER, []))

    assert lines[0].startswith(Delimiter.COMMENT_START)

def test_handle_given_a_valid_mnemonic_should_set_the_base_types_to_the_block(monkeypatch: MonkeyPatch):
    LOWER_BOUND = 1
    UPPER_BOUND = 4
    BASE_TYPES = { "base 1", "base 2" }
    MNEMONIC = _get_mnemonic(_QUERY_TYPE)
    FILTER = create_filter(f"{Operand.BASE_TYPE} {Delimiter.RULE_START}{ECON} {MNEMONIC} {LOWER_BOUND} {UPPER_BOUND}")
    ninja_mock = FunctionMock(monkeypatch, ninja.get_bases, BASE_TYPES)

    lines = econ.handle(FILTER.blocks[0], Context(FILTER, []))

    assert ninja_mock.received(_QUERY_TYPE, _LEAGUE_NAME, ValueRange(LOWER_BOUND, UPPER_BOUND))
    for base_type in BASE_TYPES:
        assert f'"{base_type}"' in lines[0]

def _get_mnemonic(query_type: QueryType):
    return next(mnemonic
        for mnemonic, query_types in _QUERY_TYPES_BY_MNEMONIC.items()
        if query_type in query_types)
    