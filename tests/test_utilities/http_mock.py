import utils
from pytest import MonkeyPatch

class HttpMock:
    """Class which monkey patches the `utils` HTTP method functions."""
    def __init__(self, monkeypatch: MonkeyPatch, get_return_value: dict):
        self.last_url_queried = None
        self.last_resource_descriptor_for_error = None
        self.get_return_value = get_return_value
        monkeypatch.setattr(utils, "http_get", self._mock_http_get)
    
    def _mock_http_get(self, url: str, resource_description_for_error: str):
        self.last_url_queried = url
        self.last_resource_descriptor_for_error = resource_description_for_error
        return self.get_return_value