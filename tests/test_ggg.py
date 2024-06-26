import pytest, ggg, web
from core import ExpectedError
from pytest import MonkeyPatch
from test_utilities import WebGetMock
from ggg.functions import _LeagueIndex, _LEAGUES_URL, _LEAGUE_ID_FIELD, _LEAGUE_NOT_FOUND_ERROR, _TEMP, _HARDCORE, _STANDARD, _RUTHLESS, _ERROR_PART_SEPARATOR

_LEAGUES = [
    (True, False, False, _LeagueIndex.STANDARD),
    (True, True, False, _LeagueIndex.HARDCORE_STANDARD),
    (True, False, True, _LeagueIndex.RUTHLESS_STANDARD),
    (True, True, True, _LeagueIndex.RUTHLESS_HARDCORE_STANDARD),
    (False, False, False, _LeagueIndex.SOFTCORE_TEMP),
    (False, True, False, _LeagueIndex.HARDCORE_TEMP),
    (False, False, True, _LeagueIndex.RUTHLESS_SOFTCORE_TEMP),
    (False, True, True, _LeagueIndex.RUTHLESS_HARDCORE_TEMP),
]
@pytest.mark.parametrize("standard, hardcore, ruthless, league_index", _LEAGUES)
def test_get_league_name_given_league_flags_should_return_the_correct_league(
    monkeypatch: MonkeyPatch, standard: bool, hardcore: bool, ruthless: bool, league_index: _LeagueIndex):
    
    LEAGUES = _get_leagues_up_to_index(league_index)
    get_mock = WebGetMock(monkeypatch, LEAGUES)

    league_name = ggg.get_league_name(standard, hardcore, ruthless)

    assert get_mock.received(_LEAGUES_URL, web.Expiration.DAILY)
    assert league_name == LEAGUES[league_index][_LEAGUE_ID_FIELD]

_NAME_NOT_FOUND_LEAGUES = [
    (False, False, False, _TEMP),
    (True, False, False, _STANDARD),
    (False, True, False, _ERROR_PART_SEPARATOR.join([_TEMP, _HARDCORE])),
    (False, False, True, _ERROR_PART_SEPARATOR.join([_TEMP, _RUTHLESS])),
    (True, True, True, _ERROR_PART_SEPARATOR.join([_STANDARD, _HARDCORE, _RUTHLESS]))
]
@pytest.mark.parametrize("standard, hardcore, ruthless, error_part", _NAME_NOT_FOUND_LEAGUES)
def test_get_league_name_given_league_name_could_not_be_found_should_raise(
        monkeypatch: MonkeyPatch, standard: bool, hardcore: bool, ruthless: bool, error_part: str):
    
    _ = WebGetMock(monkeypatch, [])

    with pytest.raises(ExpectedError) as error:
        _ = ggg.get_league_name(standard, hardcore, ruthless)
    
    assert error.value.message == _LEAGUE_NOT_FOUND_ERROR.format(error_part)

def _get_leagues_up_to_index(index: _LeagueIndex):
    return [ {} ] * index + [ { _LEAGUE_ID_FIELD : "league name" }  ]