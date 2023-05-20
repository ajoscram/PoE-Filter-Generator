def is_float(string: str):
    """Returns `True` if a string passed in can be safely cast to a float. `False` otherwise."""
    try:
        float(string)
        return True
    except ValueError:
        return False