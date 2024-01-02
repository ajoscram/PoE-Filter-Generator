import utils
from enum import Enum
from datetime import datetime, timedelta

_EXPIRATION_FORMAT = "%d-%m-%Y"
_URL_FIELD = "url"
_IS_JSON_FIELD = "is_json"
_FILENAME_FIELD = "filename"
_EXPIRATION_DATE_FIELD = "expiration_date"

class Expiration(Enum):
    IMMEDIATE = timedelta(seconds=0)
    DAILY = timedelta(days=1, hours=1)
    WEEKLY = timedelta(weeks=1, hours=2)
    MONTHLY = timedelta(weeks=4, hours=3)

class CacheEntry:
    def __init__(self, url: str, is_json: bool, expiration_date: datetime, filename: str):
        self.url = url
        self.is_json = is_json
        self.filename = filename
        self.expiration_date = expiration_date

    @classmethod
    def create(cls, url: str, is_json: bool, expiration: Expiration):
        filename = _get_filename(is_json)
        expiration_date = datetime.now() + expiration.value
        return CacheEntry(url, is_json, expiration_date, filename)

    @classmethod
    def from_dict(cls, raw_entry: dict[str, str]):
        url: str = raw_entry[_URL_FIELD]
        is_json: bool = raw_entry[_IS_JSON_FIELD]
        filename: str = raw_entry[_FILENAME_FIELD]
        expiration_date: datetime = datetime.strptime(raw_entry[_EXPIRATION_DATE_FIELD], _EXPIRATION_FORMAT)
        return CacheEntry(url, is_json, expiration_date, filename)

    def to_dict(self):
        entry = {
            _URL_FIELD: self.url,
            _IS_JSON_FIELD: self.is_json,
            _FILENAME_FIELD: self.filename,
            _EXPIRATION_DATE_FIELD: self.expiration_date.strftime(_EXPIRATION_FORMAT)
        }
        return entry
    
    def is_stale(self):
        return datetime.now() >= self.expiration_date

def _get_filename(is_json: bool):
    name = utils.get_random_str()
    extension = "json" if is_json else "txt"
    return name + f".{extension}"