import web
from web import Expiration
from .constants import NAME_FIELD

_URL = "https://lvlvllvlvllvlvl.github.io/RePoE/item_classes.min.json"

def get_classes():
    return web.get(_URL, expiration=Expiration.MONTHLY, formatter=_format_item_class_info)

def _format_item_class_info(classes_json: dict):
    return {
        key: item_class_info
        for key, item_class_info in classes_json.items()
        if _is_item_class_info_valid(item_class_info) }

def _is_item_class_info_valid(class_info: dict):
    return NAME_FIELD in class_info and class_info[NAME_FIELD] not in [ "", None ]