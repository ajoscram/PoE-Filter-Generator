import utils
from datetime import datetime
from .expiration import Expiration

_EXPIRATION_FORMAT = "%d-%m-%Y"
_URL_FIELD = "url"
_IS_JSON_FIELD = "is_json"
_FILENAME_FIELD = "filename"
_EXPIRATION_DATE_FIELD = "expiration_date"

class FileEntry:
    """Represents metadata that is used to parse entries in a `FileCache`."""

    def __init__(self, url: str, expiration_date: datetime, is_json: bool, filename: str):
        """This constructor is used internally by this class and should be avoided.
        Use `FileEntry.create` or `FileEntry.from_dict` instead."""
        self.url = url
        self.is_json = is_json
        self.filename = filename
        self.expiration_date = expiration_date

    @classmethod
    def create(cls, url: str, expiration: Expiration, is_json: bool):
        """Creates a new `FileEntry`."""
        filename = _get_filename(is_json)
        expiration_date = datetime.now() + expiration.value
        return FileEntry(url, expiration_date, is_json, filename)

    @classmethod
    def from_dict(cls, raw_entry: dict[str]):
        """Creates a new `FileEntry` from the raw data in `raw_entry`.
        This operation is the inverse of `FileEntry.to_dict`."""
        url: str = raw_entry[_URL_FIELD]
        is_json: bool = raw_entry[_IS_JSON_FIELD]
        filename: str = raw_entry[_FILENAME_FIELD]
        expiration_date: datetime = datetime.strptime(raw_entry[_EXPIRATION_DATE_FIELD], _EXPIRATION_FORMAT)
        return FileEntry(url, expiration_date, is_json, filename)

    def to_dict(self):
        """Creates a new `dict` containing all the data in the `FileEntry`."""
        return {
            _URL_FIELD: self.url,
            _EXPIRATION_DATE_FIELD: self.expiration_date.strftime(_EXPIRATION_FORMAT),
            _FILENAME_FIELD: self.filename,
            _IS_JSON_FIELD: self.is_json }
    
    def is_stale(self):
        """Returns `True` if the `FileEntry` is stale because it's been too long since it was added.
        `False` otherwise."""
        return datetime.now() >= self.expiration_date

def _get_filename(is_json: bool):
    name = utils.get_random_str()
    extension = "json" if is_json else "txt"
    return name + f".{extension}"