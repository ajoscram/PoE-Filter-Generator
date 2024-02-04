import utils, os, random
from pytest import MonkeyPatch
from test_utilities import FunctionMock
from utils.functions import _GENERATION_CHARSET

def test_get_random_str_should_return_a_random_str(monkeypatch: MonkeyPatch):
    RANDOM_STR = "random"
    LENGTH = 5 # chosen arbitrarily
    choices_mock = FunctionMock(monkeypatch, random.choices, list(RANDOM_STR))

    random_str = utils.get_random_str(LENGTH)

    assert RANDOM_STR == random_str
    assert choices_mock.received(_GENERATION_CHARSET, k=LENGTH)

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