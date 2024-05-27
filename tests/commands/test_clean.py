import pytest, web, console
from pytest import MonkeyPatch
from test_utilities import FunctionMock
from commands import clean
from commands.clean import CACHE_DELETED_MESSAGE, CACHE_NOT_DELETED_MESSAGE

@pytest.mark.parametrize("cache_exists", [ True, False ])
def test_execute_should_delete_the_cache_and_display_the_correct_message(monkeypatch: MonkeyPatch, cache_exists: bool):
    web_clear_cache_mock = FunctionMock(monkeypatch, web.clear_cache, cache_exists, target=web)
    console_write_mock = FunctionMock(monkeypatch, console.write)

    clean.execute(None)

    assert web_clear_cache_mock.get_invocation_count() == 1
    assert console_write_mock.received(CACHE_DELETED_MESSAGE if cache_exists else CACHE_NOT_DELETED_MESSAGE)