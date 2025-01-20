import web
from web import Expiration
from .constants import Field

_URL = "https://repoe-fork.github.io/item_classes.min.json"

def get_filter_item_class(class_name: str):
    """Returns the item filter equivalent class name for `class_name`."""
    classes = _get_classes()
    return classes[class_name][Field.NAME]

def _get_classes():
    return web.get(_URL, Expiration.MONTHLY, formatter=_format_item_class_info)

def _format_item_class_info(classes_json: dict):
    return {
        key: item_class_info
        for key, item_class_info in classes_json.items()
        if _is_item_class_info_valid(item_class_info) }

def _is_item_class_info_valid(class_info: dict):
    return class_info.get(Field.NAME) not in [ "", None ]