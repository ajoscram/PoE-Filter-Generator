import pytest, os, json, shutil, utils
from datetime import datetime
from web import cache, Expiration
from pytest import MonkeyPatch
from core import FILE_ENCODING
from test_utilities import FunctionMock, OpenMock
from web.cache.file_cache import _ENTRIES_FILENAME
from web.cache.file_entry import _EXPIRATION_DATE_FIELD, _EXPIRATION_FORMAT, _URL_FIELD, _IS_JSON_FIELD, _FILENAME_FIELD

_JSON_DATA = { "some": "data" }
_TEXT_DATA = "some text"
_URL = "https://www.site.com/"

@pytest.fixture(autouse=True)
def setup():
    cache.functions._file_cache = None
    cache.functions._memory_cache = None

@pytest.fixture(autouse=True)
def open_mock(monkeypatch: MonkeyPatch):
    return OpenMock(monkeypatch)

def test_try_get_given_data_cached_in_memory_should_return_it():
    cache.functions._memory_cache = { _URL: _JSON_DATA }

    data = cache.try_get(_URL)

    assert data == _JSON_DATA

def test_try_get_given_url_not_in_cache_should_return_none(monkeypatch: MonkeyPatch):
    _ = FunctionMock(monkeypatch, json.load, [ ])
    _ = FunctionMock(monkeypatch, os.path.isfile, True)

    data = cache.try_get("https://another.url")

    assert data == None

def test_try_get_given_entry_file_cannot_be_found_should_return_none(monkeypatch: MonkeyPatch):
    ENTRY = _create_entry()
    _ = FunctionMock(monkeypatch, json.load, [ ENTRY ])
    _ = FunctionMock(monkeypatch, os.path.isfile, lambda x: _ENTRIES_FILENAME in x)

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
    monkeypatch: MonkeyPatch, open_mock: OpenMock):
    
    ENTRY = _create_entry(is_json=False)
    _ = FunctionMock(monkeypatch, os.path.isfile, True)
    _ = FunctionMock(monkeypatch, json.load, [ ENTRY ])
    open_mock.file.lines = [ _TEXT_DATA ]

    data = cache.try_get(ENTRY[_URL_FIELD])

    assert data == _TEXT_DATA

def test_add_given_json_data_should_save_it_with_its_entry(monkeypatch: MonkeyPatch):
    _ = FunctionMock(monkeypatch, os.makedirs)
    json_dump_mock = FunctionMock(monkeypatch, json.dump)
    
    cache.add(_URL, Expiration.DAILY, _JSON_DATA)

    assert cache.functions._memory_cache[_URL] == _JSON_DATA
    assert json_dump_mock.get_invocation_count() == 2
    assert json_dump_mock.received(_JSON_DATA)

def test_add_given_text_data_should_save_it_with_its_entry(monkeypatch: MonkeyPatch, open_mock: OpenMock):
    _ = FunctionMock(monkeypatch, os.makedirs)
    json_dump_mock = FunctionMock(monkeypatch, json.dump)
    
    cache.add(_URL, Expiration.DAILY, _TEXT_DATA)

    assert cache.functions._memory_cache[_URL] == _TEXT_DATA
    assert json_dump_mock.get_invocation_count() == 1
    assert open_mock.received(encoding=FILE_ENCODING)
    assert open_mock.file.got_written(_TEXT_DATA)


@pytest.mark.parametrize("cache_exists", [ True, False ])
def test_clear_cache_should_delete_the_cache_folder_and_return_if_it_did(monkeypatch: MonkeyPatch, cache_exists: bool):
    DIR = "execution_directory"
    _ = FunctionMock(monkeypatch, utils.get_execution_dir, DIR)
    path_isdir_mock = FunctionMock(monkeypatch, os.path.isdir, cache_exists)
    shutil_rmtree_mock = FunctionMock(monkeypatch, shutil.rmtree)

    result = cache.clear_cache()

    assert result == cache_exists
    assert path_isdir_mock.received(DIR)
    assert shutil_rmtree_mock.get_invocation_count() == (1 if cache_exists else 0)


def _create_entry(expiration_date: datetime | str = datetime.max, is_json: bool = True):
    return {
        _URL_FIELD: _URL,
        _IS_JSON_FIELD: is_json,
        _FILENAME_FIELD: "some/file.json",
        _EXPIRATION_DATE_FIELD: expiration_date.strftime(_EXPIRATION_FORMAT) \
            if isinstance(expiration_date, datetime) else expiration_date
    }