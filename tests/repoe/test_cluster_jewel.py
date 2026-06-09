import pytest
from pytest import MonkeyPatch
from core import ExpectedError
from repoe import cluster
from repoe.constants import Field
from test_utilities import WebGetMock
from repoe.cluster import _ENCHANT_NOT_FOUND_ERROR

_ENCHANT_NAME = "enchant name"
_STAT_TEXT = "stat text"
_CLUSTER_JEWEL = {
    Field.LARGE_CLUSTER: {
        Field.PASSIVE_SKILLS: [
            {
                Field.NAME: _ENCHANT_NAME,
                Field.STAT_TEXT: [ _STAT_TEXT ],
            },
        ]
    },
    Field.MEDIUM_CLUSTER: { Field.PASSIVE_SKILLS: [ ] },
    Field.SMALL_CLUSTER: { Field.PASSIVE_SKILLS: [ ] },
}

@pytest.fixture(autouse=True)
def get_mock(monkeypatch: MonkeyPatch):
    return WebGetMock(monkeypatch, _CLUSTER_JEWEL)

def test_get_cluster_jewel_enchant_given_stat_text_was_found_should_return_enchant_name():
    enchant = cluster.get_cluster_enchant(_STAT_TEXT)

    assert enchant == _ENCHANT_NAME

def test_get_cluster_jewel_enchant_given_stat_text_was_not_found_should_raise():
    MISSING_STAT_TEXT = "missing stat text"
    
    with pytest.raises(ExpectedError) as error:
        _ = cluster.get_cluster_enchant(MISSING_STAT_TEXT)

    assert error.value.message == _ENCHANT_NOT_FOUND_ERROR.format(MISSING_STAT_TEXT)