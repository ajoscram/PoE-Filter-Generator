import pytest, os, json, shutil
from datetime import datetime
from web import cache, Expiration
from pytest import MonkeyPatch
from test_utilities import FunctionMock, FileMock
from web.cache_entry import _EXPIRATION_DATE_FIELD, _EXPIRATION_FORMAT, _URL_FIELD, _IS_JSON_FIELD, _FILENAME_FIELD
from web.cache import _ENTRIES_FILEPATH, _DIR, _FILE_ENCODING

_JSON_DATA = { "some": "data" }
_TEXT_DATA = "some text"
_URL = "https://www.site.com/"

@pytest.fixture(autouse=True)
def setup():
    cache._entries = None

@pytest.fixture(autouse=True)
def file_mock(monkeypatch: MonkeyPatch):
    return FileMock(monkeypatch)

def test_try_get_given_url_not_in_entries_should_return_none(monkeypatch: MonkeyPatch):
    _ = FunctionMock(monkeypatch, json.load, [ ])
    _ = FunctionMock(monkeypatch, os.path.isfile, True)

    data = cache.try_get("https://another.url")

    assert data == None

def test_try_get_given_entry_file_cannot_be_found_should_return_none(monkeypatch: MonkeyPatch):
    ENTRY = _create_entry()
    _ = FunctionMock(monkeypatch, json.load, [ ENTRY ])
    _ = FunctionMock(monkeypatch, os.path.isfile, lambda x: x == _ENTRIES_FILEPATH)

    data = cache.try_get(ENTRY[_URL_FIELD])

    assert data == None

def test_try_get_given_entry_is_stale_should_return_none_and_delete_the_data(monkeypatch: MonkeyPatch):
    ENTRY = _create_entry(expiration_date="01-01-1970")
    _ = FunctionMock(monkeypatch, json.load, [ ENTRY ])
    _ = FunctionMock(monkeypatch, os.path.isfile, True)
    os_remove_mock = FunctionMock(monkeypatch, os.remove)

    data = cache.try_get(ENTRY[_URL_FIELD])

    assert data == None
    assert os_remove_mock.get_invocation_count() == 1

def test_try_get_given_entry_is_valid_should_return_the_data(monkeypatch: MonkeyPatch):
    ENTRY = _create_entry()
    _ = FunctionMock(monkeypatch, os.path.isfile, True)
    _ = FunctionMock(monkeypatch, json.load, (x for x in [ [ ENTRY ], _JSON_DATA ]))

    data = cache.try_get(ENTRY[_URL_FIELD])

    assert data == _JSON_DATA

def test_try_get_given_valid_entry_is_not_json_should_return_it_as_text(
    monkeypatch: MonkeyPatch, file_mock: FileMock):
    
    ENTRY = _create_entry(is_json=False)
    _ = FunctionMock(monkeypatch, os.path.isfile, True)
    _ = FunctionMock(monkeypatch, json.load, [ ENTRY ])
    file_mock.lines = [ _TEXT_DATA ]

    data = cache.try_get(ENTRY[_URL_FIELD])

    assert data == _TEXT_DATA

def test_add_given_json_data_should_save_it_with_its_entry(monkeypatch: MonkeyPatch):
    _ = FunctionMock(monkeypatch, os.makedirs)
    json_dump_mock = FunctionMock(monkeypatch, json.dump)
    
    cache.add(_URL, Expiration.DAILY, True, _JSON_DATA)

    assert json_dump_mock.get_invocation_count() == 2
    assert json_dump_mock.received(_JSON_DATA)

def test_add_given_text_data_should_save_it_with_its_entry(monkeypatch: MonkeyPatch, file_mock: FileMock):
    _ = FunctionMock(monkeypatch, os.makedirs)
    json_dump_mock = FunctionMock(monkeypatch, json.dump)
    
    cache.add(_URL, Expiration.DAILY, False, _TEXT_DATA)

    assert json_dump_mock.get_invocation_count() == 1
    assert file_mock.received(encoding=_FILE_ENCODING)
    assert file_mock.got_written(_TEXT_DATA)


@pytest.mark.parametrize("cache_exists", [ True, False ])
def test_clear_cache_should_delete_the_cache_folder_and_return_if_it_did(monkeypatch: MonkeyPatch, cache_exists: bool):
    path_isdir_mock = FunctionMock(monkeypatch, os.path.isdir, cache_exists)
    shutil_rmtree_mock = FunctionMock(monkeypatch, shutil.rmtree)

    result = cache.clear_cache()

    assert result == cache_exists
    assert path_isdir_mock.received(_DIR)
    assert shutil_rmtree_mock.get_invocation_count() == (1 if cache_exists else 0)


def _create_entry(expiration_date: datetime | str = datetime.max, is_json: bool = True):
    return {
        _URL_FIELD: _URL,
        _IS_JSON_FIELD: is_json,
        _FILENAME_FIELD: "some/file.json",
        _EXPIRATION_DATE_FIELD: expiration_date.strftime(_EXPIRATION_FORMAT) \
            if isinstance(expiration_date, datetime) else expiration_date
    }