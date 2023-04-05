from src.wiki.constants import CLASS_FILTER_TO_ID, Field, Operator, Table
from src.wiki.query import Query
from src.wiki.where import Where

def get_uniques(classes: list[str]):
    class_where = _get_class_where(classes)
    where = Where(Field.RARITY, Operator.EQUALS, "Unique").And(class_where)
    return Query(Table.ITEMS, [ Field.NAME, Field.CLASS, Field.BASE_ITEM ]).where(where).run()

def _get_class_where(classes: list[str]):
    classes = [ CLASS_FILTER_TO_ID[class_] for class_ in classes if class_ in CLASS_FILTER_TO_ID ]
    wheres = [ Where(Field.CLASS, Operator.EQUALS, class_) for class_ in classes ]
    class_where = wheres[0]
    for where in wheres[1:]:
        class_where.Or(where)
    return class_where