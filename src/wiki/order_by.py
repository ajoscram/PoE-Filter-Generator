from .constants import COMMA, Field, Order

class OrderBy:
    def __init__(self):
        self._order_by_entries: dict[Field, Order] = {}
    
    def With(self, field: Field, order: Order):
        self._order_by_entries[field] = order
        return self
    
    def __str__(self):
        order_by_strings = [ f"{field.value}+{self._order_by_entries[field].value}" for field in self._order_by_entries ]
        return COMMA.join(order_by_strings)