import wiki, pytest
from pytest import MonkeyPatch
from tests.test_utilities.http_mock import HttpMock
from wiki.queries import _CLASS_FOR_BASE_TYPE_NOT_FOUND_ERROR
from wiki.constants import Field
from wiki.wiki_error import WikiError

BASE_TYPE = "base type"

def test_get_class_id_for_base_type_given_the_base_type_is_found_should_return_its_class(
    monkeypatch: MonkeyPatch):
    RESULT = [ { Field.CLASS_ID.value: "CLASS" } ]
    http_mock = HttpMock(monkeypatch, RESULT)

    class_ = wiki.get_class_id_for_base_type(BASE_TYPE)

    assert len(http_mock.urls_queried) == 1
    assert BASE_TYPE in http_mock.urls_queried[0]
    assert class_ == RESULT[0][Field.CLASS_ID.value]

def test_get_class_id_for_base_type_given_a_class_is_not_found_should_raise(monkeypatch: MonkeyPatch):
    RESULT = []
    _ = HttpMock(monkeypatch, RESULT)

    with pytest.raises(WikiError) as error:
        _ = wiki.get_class_id_for_base_type(BASE_TYPE)
    
    assert error.value.message == _CLASS_FOR_BASE_TYPE_NOT_FOUND_ERROR.format(BASE_TYPE)