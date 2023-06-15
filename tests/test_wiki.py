import wiki, pytest, utils
from pytest import MonkeyPatch
from wiki.queries import _CLASS_FOR_BASE_TYPE_NOT_FOUND_ERROR
from wiki.constants import Field
from wiki.wiki_error import WikiError
from test_utilities import FunctionMock

BASE_TYPE = "base type"

def test_get_class_id_for_base_type_given_the_base_type_is_found_should_return_its_class(
    monkeypatch: MonkeyPatch):
    RESULT = [ { Field.CLASS_ID.value: "CLASS" } ]
    http_get_mock = FunctionMock(monkeypatch, utils.http_get, RESULT)

    class_ = wiki.get_class_id_for_base_type(BASE_TYPE)

    url_queried = http_get_mock.get_arg(str)
    assert BASE_TYPE in url_queried
    assert class_ == RESULT[0][Field.CLASS_ID.value]

def test_get_class_id_for_base_type_given_a_class_is_not_found_should_raise(monkeypatch: MonkeyPatch):
    EMPTY_RESULT = []
    _ = FunctionMock(monkeypatch, utils.http_get, EMPTY_RESULT)

    with pytest.raises(WikiError) as error:
        _ = wiki.get_class_id_for_base_type(BASE_TYPE)
    
    assert error.value.message == _CLASS_FOR_BASE_TYPE_NOT_FOUND_ERROR.format(BASE_TYPE)