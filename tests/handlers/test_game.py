import pytest, repoe
from core import ExpectedError, Operand, Operator, RULE_START
from handlers import game
from test_utilities import create_filter, FunctionMock
from handlers.game import NAME, _MOD_PARAM, _BASE_PARAM, _INVALID_PARAM_ERROR
from pytest import MonkeyPatch

def test_handle_given_mod_param_should_upsert_on_HasExplicitMod(monkeypatch: MonkeyPatch):
    MOD = "some mod"
    _ = FunctionMock(monkeypatch, repoe.get_mods, { MOD })
    filter = create_filter(f"{RULE_START}{NAME} {_MOD_PARAM}")

    lines = game.handle(filter, filter.blocks[0], None)

    assert len(lines) == 2
    assert lines[1] == f'{Operand.HAS_EXPLICIT_MOD} {Operator.EQUALS} "{MOD}"'

def test_handle_given_base_param_should_upsert_on_BaseType(monkeypatch: MonkeyPatch):
    BASE_TYPE_NAME = "some base"
    _ = FunctionMock(monkeypatch, repoe.get_bases, { BASE_TYPE_NAME })
    filter = create_filter(f"{RULE_START}{NAME} {_BASE_PARAM}")

    lines = game.handle(filter, filter.blocks[0], None)

    assert len(lines) == 2
    assert lines[1] == f'{Operand.BASE_TYPE} {Operator.EQUALS} "{BASE_TYPE_NAME}"'

def test_handle_given_unknown_param_should_raise():
    UNKNOWN_PARAM = "unknown_param"
    filter = create_filter(f"{RULE_START}{NAME} {UNKNOWN_PARAM}")

    with pytest.raises(ExpectedError) as error:
        _ = game.handle(filter, filter.blocks[0], None)
    
    assert error.value.line_number == 1
    assert error.value.message == _INVALID_PARAM_ERROR.format(UNKNOWN_PARAM)