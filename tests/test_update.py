import console, sys, update, json, web, pytest
from commands.update import DIRECTORY_FIELD, EXE_NAME, NOTES_FIELD, TAG_FIELD
from update import _UNEXPECTED_DATA_ERROR, EXE_DOWNLOAD_URL_FIELD
from test_utilities import FunctionMock
from pytest import MonkeyPatch
from core import ExpectedError

def test_main_given_params_should_download_the_latest_update(monkeypatch: MonkeyPatch):
    PARAMS = { EXE_DOWNLOAD_URL_FIELD: "1", DIRECTORY_FIELD: "2", TAG_FIELD: "3", NOTES_FIELD: "4" }
    _mock_argv_with_params(monkeypatch, PARAMS)
    web_download_mock = FunctionMock(monkeypatch, web.download)

    update.main()

    assert web_download_mock.received(PARAMS[EXE_DOWNLOAD_URL_FIELD], EXE_NAME)


def test_main_given_incorrect_number_of_args_should_call_console_err(monkeypatch: MonkeyPatch):
    console_err_mock = FunctionMock(monkeypatch, console.err)
    monkeypatch.setattr(sys, 'argv', []) # 0 != 2 args

    update.main()

    error: ExpectedError = console_err_mock.get_arg(ExpectedError)
    assert error.message == _UNEXPECTED_DATA_ERROR

_ERRONEOUS_PARAMS = [
    { DIRECTORY_FIELD: "2", TAG_FIELD: "3", NOTES_FIELD: "4" },
    { EXE_DOWNLOAD_URL_FIELD: "1", TAG_FIELD: "3", NOTES_FIELD: "4" },
    { EXE_DOWNLOAD_URL_FIELD: "1", DIRECTORY_FIELD: "2", NOTES_FIELD: "4" },
    { EXE_DOWNLOAD_URL_FIELD: "1", DIRECTORY_FIELD: "2", TAG_FIELD: "3" },
]
@pytest.mark.parametrize("params", _ERRONEOUS_PARAMS)
def test_main_given_a_json_param_is_missing_should_call_console_err(monkeypatch: MonkeyPatch, params: dict):
    console_err_mock = FunctionMock(monkeypatch, console.err)
    _mock_argv_with_params(monkeypatch, params)

    update.main()

    error: ExpectedError = console_err_mock.get_arg(ExpectedError)
    assert error.message == _UNEXPECTED_DATA_ERROR

def _mock_argv_with_params(monkeypatch: MonkeyPatch, json_dict: dict):
    json_dict = json.dumps(json_dict)
    monkeypatch.setattr(sys, 'argv', [ "program.py", json_dict ])