import utils
from pytest import MonkeyPatch

class HttpMock:
    """Class which monkey patches the `utils` HTTP method functions."""
    def __init__(self, monkeypatch: MonkeyPatch, get_return_value: dict):
        self.urls_queried = []
        self.resource_descriptions = []
        self.get_return_value = get_return_value
        monkeypatch.setattr(utils, utils.http_get.__name__, self._mock_http_get)
    
    def _mock_http_get(self, url: str, resource_description_for_error: str):
        self.urls_queried += [ url ]
        self.resource_descriptions += [ resource_description_for_error ]
        return self.get_return_value