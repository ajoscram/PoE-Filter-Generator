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
    
    def __call__(self, *args, **kwargs):
        result = super().__call__(*args, **kwargs)

        if _FORMATTER in kwargs:
            return kwargs[_FORMATTER](result)
        
        if len(args) >= 3: # the formatter is always the 3rd parameter
            return args[2](result)
        
        return result