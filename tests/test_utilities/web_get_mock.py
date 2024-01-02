import web
from .function_mock import FunctionMock
from pytest import MonkeyPatch

_FORMATTER = "formatter"

class WebGetMock(FunctionMock):
    """Mocks the `web.get` function, ensuring the `formatter` is applied on the data returned."""

    def __init__(self, monkeypatch: MonkeyPatch, result):
        """The `result` parameter will be returned from the `web.get` invocation.
        If `formatter` is passed when `web.get` is called, it is applied to the `result` before returning."""
        super().__init__(monkeypatch, web.get, result)
    
    def _mock_function(self, *args, **kwargs):
        result = super()._mock_function(*args, **kwargs)
        return kwargs[_FORMATTER](result) if _FORMATTER in kwargs else result