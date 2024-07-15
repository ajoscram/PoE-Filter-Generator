import console, sys, update, json, web, pytest, utils
from commands.update import DIRECTORY_FIELD, EXE_NAME, NOTES_FIELD, TAG_FIELD
from update import _UNEXPECTED_DATA_ERROR, EXE_DOWNLOAD_URL_FIELD
from test_utilities import FunctionMock
from pytest import MonkeyPatch
from core import ExpectedError, ERROR_EXIT_CODE

@pytest.fixture()
def console_err_mock(monkeypatch: MonkeyPatch):
    return FunctionMock(monkeypatch, console.err)

@pytest.fixture()
def sys_exit_mock(monkeypatch: MonkeyPatch):
    return FunctionMock(monkeypatch, sys.exit)

def test_main_given_params_should_download_the_latest_update(monkeypatch: MonkeyPatch):
    PARAMS = { EXE_DOWNLOAD_URL_FIELD: "1", DIRECTORY_FIELD: "2", TAG_FIELD: "3", NOTES_FIELD: "4" }
    web_download_mock = FunctionMock(monkeypatch, web.download)
    web_clear_cache_mock = FunctionMock(monkeypatch, web.clear_cache, target=web)
    params = _get_encoded_params(PARAMS)

    update.main(params)

    assert web_download_mock.received(PARAMS[EXE_DOWNLOAD_URL_FIELD], EXE_NAME)
    assert web_clear_cache_mock.get_invocation_count() == 1


def test_main_given_incorrect_number_of_args_should_print_error_and_exit(
    console_err_mock: FunctionMock, sys_exit_mock: FunctionMock):

    update.main([])

    error: ExpectedError = console_err_mock.get_arg(ExpectedError)
    assert error.message == _UNEXPECTED_DATA_ERROR
    assert sys_exit_mock.received(ERROR_EXIT_CODE)

def test_main_given_unparseable_json_should_print_error_and_exit(
    console_err_mock: FunctionMock, sys_exit_mock: FunctionMock):

    INVALID_JSON = "{ invalid json"
    params = _get_encoded_params(INVALID_JSON)

    update.main(params)

    error: ExpectedError = console_err_mock.get_arg(ExpectedError)
    assert error.message == _UNEXPECTED_DATA_ERROR
    assert sys_exit_mock.received(ERROR_EXIT_CODE)

_ERRONEOUS_PARAMS = [
    { DIRECTORY_FIELD: "2", TAG_FIELD: "3", NOTES_FIELD: "4" },
    { EXE_DOWNLOAD_URL_FIELD: "1", TAG_FIELD: "3", NOTES_FIELD: "4" },
    { EXE_DOWNLOAD_URL_FIELD: "1", DIRECTORY_FIELD: "2", NOTES_FIELD: "4" },
    { EXE_DOWNLOAD_URL_FIELD: "1", DIRECTORY_FIELD: "2", TAG_FIELD: "3" },
]
@pytest.mark.parametrize("param_dict", _ERRONEOUS_PARAMS)
def test_main_given_a_json_param_is_missing_should_call_console_err(
    console_err_mock: FunctionMock, sys_exit_mock: FunctionMock, param_dict: dict):

    params = _get_encoded_params(param_dict)

    update.main(params)

    error: ExpectedError = console_err_mock.get_arg(ExpectedError)
    assert error.message == _UNEXPECTED_DATA_ERROR
    assert sys_exit_mock.received(ERROR_EXIT_CODE)

def _get_encoded_params(json_dict_or_str: dict | str):
    json_dict_or_str = json.dumps(json_dict_or_str) \
        if isinstance(json_dict_or_str, dict) else json_dict_or_str
    return [ utils.b64_encode(json_dict_or_str) ]