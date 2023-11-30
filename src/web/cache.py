import os, json, utils, shutil
from .cache_entry import CacheEntry, Expiration

_DIR = utils.get_execution_dir("cache")
_ENTRIES_FILEPATH = os.path.join(_DIR, "_entries.json")

_entries: dict[str, CacheEntry] = None

def try_get(url: str):
    """Attempts to get an item previously added to the cache via it's `url`."""
    global _entries
    _entries = _entries or _get_entries()
    
    if not url in _entries:
        return None
    
    entry = _entries[url]
    filepath = os.path.join(_DIR, entry.filename)
    
    if not os.path.isfile(filepath):
        del _entries[url]
        return None

    if entry.is_stale():
        del _entries[url]
        os.remove(filepath)
        return None

    return _load_file(filepath, entry.is_json)
    
def add(url: str, expiration: Expiration, is_json: bool, data):
    """Adds a new `data` item to the cache, which can be obtained later via it's URL.
    * `expiration` determines how long the item will be considered valid for.
    * `is_json` determines if the item should be stored and returned as a dictionary.
    If not, the cache will save and return the item as a string."""
    global _entries
    _entries = _entries or _get_entries()
    
    entry = CacheEntry.create(url, is_json, expiration)
    filepath = os.path.join(_DIR, entry.filename)
    
    _entries[url] = entry
    _save_entries(_entries)
    _save_file(filepath, data, is_json)

def clear_cache():
    """Removes all cache files and entries from disk.
    Returns `True` is the cache is found. `False` otherwise."""
    if not os.path.isdir(_DIR):
        return False
    
    shutil.rmtree(_DIR)
    return True

def _get_entries():
    if not os.path.isfile(_ENTRIES_FILEPATH):
        return {}

    raw_entries: list[dict[str, str]] = _load_file(_ENTRIES_FILEPATH)
    entries = [ CacheEntry.from_dict(entry) for entry in raw_entries ]
    return { entry.url: entry for entry in entries }

def _save_entries(entries: dict[str, CacheEntry]):
    os.makedirs(_DIR, exist_ok=True)
    raw_entries = [ entry.to_dict() for _, entry in entries.items() ]
    _save_file(_ENTRIES_FILEPATH, raw_entries)

def _save_file(filepath: str, data, is_json: bool = True):
    with open(filepath, "w") as file:
        if is_json:
            json.dump(data, file, indent=4)
        else:
            file.write(data)

def _load_file(filepath: str, is_json: bool = True):
    with open(filepath, "r") as file:
        return json.load(file) if is_json else file.read()