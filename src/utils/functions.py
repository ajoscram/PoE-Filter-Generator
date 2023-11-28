import random, string, sys, os

_GENERATION_CHARSET = string.ascii_letters + string.digits

def get_random_str(length: int = 20):
    """Returns a random string of numbers and upper/lowercase letters of `length` size.
    The default 20 characters length was selected arbitrarily as 'long enough'."""
    return "".join(random.choices(_GENERATION_CHARSET, k=length))

def get_execution_dir(*subdirs_to_append: str):
    """Gets the directory where this script or executable is.
    This is different from the current process directory, which is obtained from `os.get_cwd()`.
    Additional subdirectories can be appended to the resulting directory."""
    execution_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
    return os.path.join(execution_dir, *subdirs_to_append)