from .wiki_error import WikiError
from .constants import Field, Operator, Table, ID_TO_FILTER_CLASSES_DICT, FILTER_TO_ID_CLASSES_DICT
from .query import Query
from .where import Where

_CLASS_FOR_BASE_TYPE_NOT_FOUND_ERROR = "A suitable class for base type '{0}' could not be found on the Wiki."

def get_class_id_for_base_type(base_type: str):
    """Returns the class associated to the `base_type` received.
    NOTE: This returns an internal GGG class_id, NOT a regular filter class."""
    where = Where(Field.BASE_ITEM, Operator.EQUALS, base_type)
    results = Query(Table.ITEMS, [ Field.CLASS_ID ]).where(where).limit(1).run()
    if len(results) == 0:
        raise WikiError(_CLASS_FOR_BASE_TYPE_NOT_FOUND_ERROR.format(base_type))
    return results[0][Field.CLASS_ID.value]

def try_translate_class(class_: str, viceversa: bool = False):
    """Tries to translate a class from a filter class to a GGG API internal class ID, or vice-versa.
    Returns the same class passed in for translation upon failure."""
    dictionary_for_translation = ID_TO_FILTER_CLASSES_DICT if viceversa else FILTER_TO_ID_CLASSES_DICT
    return dictionary_for_translation[class_] if class_ in dictionary_for_translation else class_