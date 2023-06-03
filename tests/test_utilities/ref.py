class Ref:
    """This class is a reference wrapper to a variable inside it.
    Used to reference variables in closures on tests."""
    def __init__(self, value = None):
        self.value = value
    
    def __eq__(self, other):
        if isinstance(other, Ref):
            other = other.value
        return self.value == other
    
    def __repr__(self):
        return str(self.value)