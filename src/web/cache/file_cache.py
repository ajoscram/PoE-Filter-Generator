import os, json, shutil
from core import FILE_ENCODING
from .file_entry import FileEntry
from .expiration import Expiration

_ENTRIES_FILENAME = "_entries.json"

class FileCache:
    """Caches data in storage."""

    def __init__(self, directory: str):
        """`dir` is the directory where the cache is to be created."""
        self._dir = directory
        self._entries_filepath = os.path.join(directory, _ENTRIES_FILENAME)
        self._entries: dict[str, FileEntry] = self._load_entries()

    def __contains__(self, url: str):
        """Returns `True` if `url` has an item registered within the cache. False otherwise."""
        if url not in self._entries:
            return False
        
        entry = self._entries[url]
        filepath = os.path.join(self._dir, entry.filename)
        
        if not os.path.isfile(filepath):
            del self._entries[url]
            return False
        
        if entry.is_stale():
            del self._entries[url]
            os.remove(filepath)
            return False
        
        return True

    def __getitem__(self, url: str):
        """Attempts to get an item previously added to the cache via it's `url`."""        
        entry = self._entries[url]
        filepath = os.path.join(self._dir, entry.filename)
        return _load_file(filepath, entry.is_json)
    
    def add(self, url: str, expiration: Expiration, data: str | dict | list):
        """Adds a new `data` item to the cache, which can be obtained later via it's URL.
        * `expiration` determines how long the item will be considered valid for."""
        is_json = not isinstance(data, str)
        entry = FileEntry.create(url, expiration, is_json)
        filepath = os.path.join(self._dir, entry.filename)
        
        os.makedirs(self._dir, exist_ok=True)
        _save_file(filepath, data, is_json)
        self._update_entries(entry)

    def clear(self):
        """Removes all cache files and entries from disk.
        Returns `True` is the cache is found. `False` otherwise."""
        if not os.path.isdir(self._dir):
            return False

        shutil.rmtree(self._dir)
        return True

    def _load_entries(self):
        if not os.path.isfile(self._entries_filepath):
            return {}
        raw_entries: list[dict[str, str]] = _load_file(self._entries_filepath)
        entries = [ FileEntry.from_dict(entry) for entry in raw_entries ]
        return { entry.url: entry for entry in entries }

    def _update_entries(self, entry: FileEntry):
        self._entries[entry.url] = entry
        raw_entries = [ entry.to_dict() for entry in self._entries.values() ]
        _save_file(self._entries_filepath, raw_entries)

def _save_file(filepath: str, data: str | dict | list, is_json: bool = True):
    with open(filepath, "w", encoding=FILE_ENCODING) as file:
        if is_json:
            json.dump(data, file, indent=4)
        else:
            file.write(data)

def _load_file(filepath: str, is_json: bool = True):
    with open(filepath, "r", encoding=FILE_ENCODING) as file:
        return json.load(file) if is_json else file.read()