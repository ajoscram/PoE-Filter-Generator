from .constants import FILTER_TO_INTERNAL_CLASSES, Field, Operator, Table
from .query import Query
from .where import Where

def get_uniques(filter_classes: list[str]):
    class_where = _get_class_where(filter_classes)
    where = Where(Field.RARITY, Operator.EQUALS, "Unique").And(class_where)
    return Query(Table.ITEMS, [ Field.NAME, Field.CLASS, Field.BASE_ITEM ]).where(where).run()

def _get_class_where(classes: list[str]):
    classes = [ FILTER_TO_INTERNAL_CLASSES[class_] for class_ in classes if class_ in FILTER_TO_INTERNAL_CLASSES ]
    wheres = [ Where(Field.CLASS, Operator.EQUALS, class_) for class_ in classes ]
    class_where = wheres[0]
    for where in wheres[1:]:
        class_where.Or(where)
    return class_where