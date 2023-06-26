import pytest, ggg, utils
from pytest import MonkeyPatch
from test_utilities import FunctionMock
from ggg.league import _LEAGUES_URL, _LEAGUES_ERROR_DESCRIPTOR, _LEAGUE_ID_FIELD, _LeagueIndex

_LEAGUES = [
    (True, False, False, _LeagueIndex.STANDARD),
    (True, True, False, _LeagueIndex.HARDCORE_STANDARD),
    (True, False, True, _LeagueIndex.RUTHLESS_STANDARD),
    (True, True, True, _LeagueIndex.RUTHLESS_HARDCORE_STANDARD),
    (False, False, False, _LeagueIndex.TEMP_SOFTCORE),
    (False, True, False, _LeagueIndex.TEMP_HARDCORE),
    (False, False, True, _LeagueIndex.RUTHLESS_SOFTCORE),
    (False, True, True, _LeagueIndex.RUTHLESS_HARDCORE),
]
@pytest.mark.parametrize("standard, hardcore, ruthless, league_index", _LEAGUES)
def test_get_league_name_given_league_flags_should_return_the_correct_league(
    monkeypatch: MonkeyPatch, standard: bool, hardcore: bool, ruthless: bool, league_index: _LeagueIndex):
    LEAGUE_NAME = "league name"
    QUERY_RESULT = { league_index.value : { _LEAGUE_ID_FIELD : LEAGUE_NAME } }
    http_get_mock = FunctionMock(monkeypatch, utils.http_get, QUERY_RESULT)

    league_name = ggg.get_league_name(standard, hardcore, ruthless)

    assert http_get_mock.received(_LEAGUES_URL, _LEAGUES_ERROR_DESCRIPTOR)
    assert league_name == LEAGUE_NAME