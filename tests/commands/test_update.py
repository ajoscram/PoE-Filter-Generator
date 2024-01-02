import pytest, web, os, utils
from pytest import MonkeyPatch
from test_utilities import FunctionMock, WebGetMock
from commands.update import _ASSET_NAME_FIELD, _ASSETS_FIELD, _FAILED_TO_FIND_DOWNLOAD_URL_ERROR, _UPDATER_EXE_NAME, ASSET_DOWNLOAD_URL_FIELD, DIRECTORY_FIELD, EXE_NAME, NOTES_FIELD, TAG_FIELD
from core import ExpectedError
from commands import update

_EXE_DIR = "curr_dir"

@pytest.fixture(autouse=True)
def get_execution_dir_mock(monkeypatch: MonkeyPatch):
    _ = FunctionMock(monkeypatch, utils.get_execution_dir, _EXE_DIR)

_RELEASES_MISSING_ASSET = [
    (
        {
            _ASSETS_FIELD: [  { _ASSET_NAME_FIELD: _UPDATER_EXE_NAME, ASSET_DOWNLOAD_URL_FIELD: "url" } ]
        },
        EXE_NAME
    ),
    (
        {
            _ASSETS_FIELD: [  { _ASSET_NAME_FIELD: EXE_NAME, ASSET_DOWNLOAD_URL_FIELD: "url" } ]
        },
        _UPDATER_EXE_NAME
    ),
]
@pytest.mark.parametrize("release, missing_asset_name", _RELEASES_MISSING_ASSET)
def test_execute_given_a_download_url_is_not_in_release_should_raise(
    monkeypatch: MonkeyPatch, release: dict, missing_asset_name: str):
    
    _ = WebGetMock(monkeypatch, release)

    with pytest.raises(ExpectedError) as error:
        update.execute(None)

    assert error.value.message == _FAILED_TO_FIND_DOWNLOAD_URL_ERROR.format(missing_asset_name)

def test_execute_given_a_release_is_found_should_download_and_execute_the_updater(monkeypatch: MonkeyPatch):
    UPDATER_FILEPATH = "updater_filepath"
    UPDATER_URL = "updater_url"
    EXE_URL = "EXE_URL"
    RELEASE = {
        NOTES_FIELD: "notes",
        TAG_FIELD: "tag",
        _ASSETS_FIELD: [
            { _ASSET_NAME_FIELD: _UPDATER_EXE_NAME, ASSET_DOWNLOAD_URL_FIELD: UPDATER_URL },
            { _ASSET_NAME_FIELD: EXE_NAME, ASSET_DOWNLOAD_URL_FIELD: EXE_URL },
        ]
    }
    _ = WebGetMock(monkeypatch, RELEASE)
    os_path_join_mock = FunctionMock(monkeypatch, os.path.join, UPDATER_FILEPATH)
    web_download_mock = FunctionMock(monkeypatch, web.download)
    os_execl_mock = FunctionMock(monkeypatch, os.execl)

    update.execute(None)

    assert os_path_join_mock.received(_EXE_DIR, _UPDATER_EXE_NAME)
    assert web_download_mock.received(UPDATER_URL, _EXE_DIR, _UPDATER_EXE_NAME)
    assert os_execl_mock.received(UPDATER_FILEPATH, UPDATER_FILEPATH)
    
    updater_params_string = os_execl_mock.get_arg(str, n = 2)
    assert ASSET_DOWNLOAD_URL_FIELD in updater_params_string
    assert EXE_URL in updater_params_string
    assert NOTES_FIELD in updater_params_string
    assert RELEASE[NOTES_FIELD] in updater_params_string
    assert TAG_FIELD in updater_params_string
    assert RELEASE[TAG_FIELD] in updater_params_string
    assert DIRECTORY_FIELD in updater_params_string
    assert _EXE_DIR in updater_params_string