import web, re
from core import ExpectedError
from web import Expiration

_BASE_ITEMS_URL = "https://lvlvllvlvllvlvl.github.io/RePoE/base_items.min.json"
_ITEM_CLASSES_URL = "https://lvlvllvlvllvlvl.github.io/RePoE/item_classes.min.json"

_NAME_FIELD = "name"
_BASE_TYPE_DOMAIN_FIELD = "domain"
_BASE_TYPE_CLASS_FIELD = "item_class"
_BASE_TYPE_RELEASE_STATE = "release_state"
_BASE_TYPE_FILTER_ITEM_CLASS = "filter_item_class"

_UNIQUE_ONLY_RELEASE_STATE = "unique_only"
_RELEASED_BASE_TYPE_RELEASE_STATE = "released"
_INVALID_BASE_TYPE_DOMAINS = [ "undefined", "map_device", "watchstone" ]
_INVALID_BASE_TYPE_ID_PATTERNS = [
    # Deprecated or duplicated base types
    "Royale", "Quiver\\d+", "Talisman\\d*_\\d*_[^1]",
    # Previous map series identifiers
    "Shaped", "MapTier", "Map2Tier", "MapTier","MapAtlas", "MapWorldsHarbingerMid", "MapWorldsHarbingerHigh" ]

_BASE_NAME_NOT_FOUND_ERROR = "The base item name '{0}' could not be identified when attempting to get its class name."

def get_class_for_base(base_name: str, prefix: bool = False):
    """Returns the item class name associated to the `base_name` type received.
    If `prefix` is `True` the `base_name` the first base name found that starts with `base_name` will be used instead."""

    # hardcoded result for pieces as they cannot currently be obtained from RePoE
    # left untested because this should be removed eventually
    if "Piece" in base_name:
        return "Pieces"

    bases_info: dict[str] = web.get(_BASE_ITEMS_URL, expiration=Expiration.MONTHLY, formatter=_format_bases_info)

    if prefix:
        base_name = _get_full_base_name(base_name, bases_info.keys())

    if base_name not in bases_info:
        raise ExpectedError(_BASE_NAME_NOT_FOUND_ERROR.format(base_name))

    return bases_info[base_name][_BASE_TYPE_FILTER_ITEM_CLASS]

def _get_full_base_name(prefix: str, base_names: list[str]):
    prefix_lowered = prefix.lower()
    
    for base_name in base_names:
        if base_name.lower().startswith(prefix_lowered):
            return base_name
    
    return prefix

def _format_bases_info(bases_json: dict[str, dict]):
    item_classes = web.get(_ITEM_CLASSES_URL, expiration=Expiration.MONTHLY, formatter=_format_item_class_info)
    return {
        base_info[_NAME_FIELD]: _get_formatted_base_info(base_info, item_classes)
        for base_id, base_info in bases_json.items()
        if _is_base_valid(base_id, base_info) }

def _get_formatted_base_info(base_info: dict[str], item_classes: dict[str]):
    item_class_name = base_info[_BASE_TYPE_CLASS_FIELD]
    filter_item_class_name = item_classes[item_class_name][_NAME_FIELD]
    base_info[_BASE_TYPE_FILTER_ITEM_CLASS] = filter_item_class_name
    return base_info

def _format_item_class_info(classes_json: dict):
    return {
        key: item_class_info
        for key, item_class_info in classes_json.items()
        if _is_item_class_info_valid(item_class_info) }

def _is_base_valid(base_id: str, base_info: dict[str]):
    if base_info[_BASE_TYPE_RELEASE_STATE] == _UNIQUE_ONLY_RELEASE_STATE:
        return True
    return _is_base_id_valid(base_id) and _is_base_info_valid(base_info)

def _is_base_info_valid(base_info: dict):
    released = base_info[_BASE_TYPE_RELEASE_STATE] == _RELEASED_BASE_TYPE_RELEASE_STATE
    valid_domain = base_info[_BASE_TYPE_DOMAIN_FIELD] not in _INVALID_BASE_TYPE_DOMAINS
    return released and valid_domain

def _is_base_id_valid(base_id: str):
    base_name = base_id.split("/")[-1]
    return all(re.search(pattern, base_name) == None for pattern in _INVALID_BASE_TYPE_ID_PATTERNS)

def _is_item_class_info_valid(class_info: dict):
    return _NAME_FIELD in class_info and class_info[_NAME_FIELD] not in [ "", None ]