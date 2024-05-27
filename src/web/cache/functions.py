import utils
from .expiration import Expiration
from .file_cache import FileCache

_CACHE_DIR = "cache"

_file_cache: FileCache = None
_memory_cache: dict[str, str | dict | list] = None

def try_get(url: str):
    """Get an item previously added to the cache via it's `url`.
    If the item cannot be found, `None` is returned instead."""
    (_memory_cache, _file_cache) = _get_caches()

    if url in _memory_cache:
        return _memory_cache[url]

    if url in _file_cache:
        _memory_cache[url] = _file_cache[url]
        return _memory_cache[url]

    return None
    
def add(url: str, expiration: Expiration, data: str | dict | list):
    """Adds a new `data` item to the cache, which can be obtained later via it's URL.
    * `expiration` determines how long the item will be considered valid for."""
    (_memory_cache, _file_cache) = _get_caches()
    _memory_cache[url] = data
    _file_cache.add(url, expiration, data)

def clear_cache():
    """Removes all cache files and entries from disk.
    Returns `True` is the cache is found. `False` otherwise."""
    (_, _file_cache) = _get_caches()
    return _file_cache.clear()

def _get_caches():
    global _memory_cache, _file_cache
    _memory_cache = _memory_cache or {}
    _file_cache = _file_cache or FileCache(utils.get_execution_dir(_CACHE_DIR))
    return (_memory_cache, _file_cache)