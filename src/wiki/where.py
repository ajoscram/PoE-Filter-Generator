from .constants import Field, Operator

_AND = "AND"
_OR = "OR"

class Where:
    def __init__(self, field: Field, operator: Operator, value: str | int):
        self._field = field
        self._operator = operator
        self._value = value
        self._chain: list[Where | str] = []
            
    def And(self, where):
        self._chain += [ _AND, where ]
        return self

    def Or(self, where):
        self._chain += [ _OR, where ]
        return self
    
    def __str__(self):
        value = f"\"{self._value}\"" if type(self._value) == str else str(self._value)

        if len(self._chain) == 0:
            return f"{self._field.value} {self._operator.value} {value}"
        
        chain = " ".join([ str(item) for item in self._chain ])
        return f"({self._field.value} {self._operator.value} {value} {chain})"
        