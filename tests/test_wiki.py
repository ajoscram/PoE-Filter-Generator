import wiki, pytest, web
from pytest import MonkeyPatch
from wiki.functions import _CLASS_FOR_BASE_TYPE_NOT_FOUND_ERROR
from wiki.constants import Field, Table
from wiki.wiki_error import WikiError
from wiki.query import Query
from test_utilities import FunctionMock

_BASE_TYPE = "base type"

@pytest.fixture()
def get_mock(monkeypatch: MonkeyPatch):
    return FunctionMock(monkeypatch, web.get)

def test_get_class_id_for_base_type_given_the_base_type_is_found_should_return_its_class(get_mock: FunctionMock):
    RESULT = [ { Field.CLASS_ID.value: "CLASS" } ]
    get_mock.result = RESULT

    class_ = wiki.get_class_id_for_base_type(_BASE_TYPE)

    url_queried = get_mock.get_arg(str)
    assert _BASE_TYPE in url_queried
    assert class_ == RESULT[0][Field.CLASS_ID.value]

def test_get_class_id_for_base_type_given_a_class_is_not_found_should_raise(get_mock: FunctionMock):
    get_mock.result = []

    with pytest.raises(WikiError) as error:
        _ = wiki.get_class_id_for_base_type(_BASE_TYPE)
    
    assert error.value.message == _CLASS_FOR_BASE_TYPE_NOT_FOUND_ERROR.format(_BASE_TYPE)

def test_any_query_should_expire_weekly(get_mock: FunctionMock):
    get_mock.result = [] # result doesn't matter but must be non-null
    query = Query(Table.ITEMS, Field.BASE_ITEM) # table and field chosen arbitrarily

    query.run()

    assert get_mock.received(expiration=web.Expiration.WEEKLY)