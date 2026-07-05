import utils, os, random, pytest
from pytest import MonkeyPatch
from test_utilities import FunctionMock
from core import Delimiter, ExpectedError
from utils.functions import _RANDOM_STR_GENERATION_CHARSET, _KVP_EMPTY_ERROR, _KVP_EQUALS_COUNT_ERROR, _KVP_MISSING_KEY_ERROR, _KVP_MISSING_VALUE_ERROR

def test_get_random_str_should_return_a_random_str(monkeypatch: MonkeyPatch):
    RANDOM_STR = "random"
    LENGTH = 5 # chosen arbitrarily
    choices_mock = FunctionMock(monkeypatch, random.choices, list(RANDOM_STR))

    random_str = utils.get_random_str(LENGTH)

    assert RANDOM_STR == random_str
    assert choices_mock.received(_RANDOM_STR_GENERATION_CHARSET, k=LENGTH)

def test_get_execution_dir_should_return_the_current_executable_directory(monkeypatch: MonkeyPatch):
    CURR_DIR = "curr_dir"
    SUB_DIR = "sub_dir"
    abspath_mock = FunctionMock(monkeypatch, os.path.abspath, lambda x: x)
    _ = FunctionMock(monkeypatch, os.path.dirname, CURR_DIR)

    exec_dir = utils.get_execution_dir(SUB_DIR)

    assert abspath_mock.get_invocation_count() == 1
    assert CURR_DIR in exec_dir
    assert SUB_DIR in exec_dir

def test_b64_encode_and_decode_should_be_symmetrical():
    TEXT = "some text to encode with \\\"escaped characters\\\""

    encoded_text = utils.b64_encode(TEXT)
    decoded_text = utils.b64_decode(encoded_text)

    assert decoded_text == TEXT

def test_parse_key_value_list_should_return_key_value_pairs():
    KEY_1 = "key_1"
    KEY_2 = "key_2"
    VALUE_1 = "value_1"
    VALUE_2 = "value_2"
    TEXT = f"{KEY_1} {Delimiter.PAIR_SEPARATOR} {VALUE_1}{Delimiter.LIST_ENTRY_SEPARATOR} {KEY_2} {Delimiter.PAIR_SEPARATOR} {VALUE_2}"

    pairs = utils.parse_key_value_list(TEXT)

    assert pairs[0][0] == KEY_1
    assert pairs[0][1] == VALUE_1
    assert pairs[1][0] == KEY_2
    assert pairs[1][1] == VALUE_2

@pytest.mark.parametrize("text", [ "", "    ", "\t" ])
def test_parse_key_value_list_given_whitespace_should_return_empty_list(text: str):
    pairs = utils.parse_key_value_list(text)
    
    assert len(pairs) == 0

def test_parse_key_value_list_given_empty_kvp_should_raise():
    LINE_NUMBER = 1
    TEXT = "key=value,,key2=value2"

    with pytest.raises(ExpectedError) as error:
        utils.parse_key_value_list(TEXT, LINE_NUMBER)
    
    assert _KVP_EMPTY_ERROR.format(TEXT) in error.value.message
    assert error.value.line_number == LINE_NUMBER

@pytest.mark.parametrize("key, value, expected_error", [
    (f"{Delimiter.PAIR_SEPARATOR}", "", _KVP_EQUALS_COUNT_ERROR),
    ("", "value", _KVP_MISSING_KEY_ERROR),
    ("key", "", _KVP_MISSING_VALUE_ERROR),
])
def test_parse_key_value_list_given_kvp_format_error_should_raise(key: str, value: str, expected_error: str):
    LINE_NUMBER = 1
    text = f"{key} {Delimiter.PAIR_SEPARATOR} {value}"

    with pytest.raises(ExpectedError) as error:
        utils.parse_key_value_list(text, LINE_NUMBER)

    assert expected_error.format(text) in error.value.message
    assert error.value.line_number == LINE_NUMBER