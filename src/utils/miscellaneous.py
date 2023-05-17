def is_float(string: str):
    """Checks if a string passed in can be safely cast to a float."""
    try:
        float(string)
        return True
    except ValueError:
        return False