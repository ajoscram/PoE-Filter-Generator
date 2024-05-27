import pytest
from repoe import class_
from pytest import MonkeyPatch
from test_utilities import WebGetMock
from repoe.constants import Field

_CLASS_NAME = "class_id"
_FILTER_CLASS_NAME = "class_name"

@pytest.fixture(autouse=True)
def get_mock(monkeypatch: MonkeyPatch):
    return WebGetMock(monkeypatch, None)

def test_get_filter_item_class_given_class_name_should_return_filter_class_name(get_mock: WebGetMock):
    get_mock.result = _create_classes()

    filter_class_name = class_.get_filter_item_class(_CLASS_NAME)

    assert filter_class_name == _FILTER_CLASS_NAME

def _create_classes(class_name: str = _CLASS_NAME, filter_class_name: str = _FILTER_CLASS_NAME):
    return { class_name: { Field.NAME.value: filter_class_name } }
