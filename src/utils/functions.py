import random, string, sys, os, base64

_GENERATION_CHARSET = string.ascii_letters + string.digits

def get_random_str(length: int = 20):
    """Returns a random string of numbers and upper/lowercase letters of `length` size.
    The default 20 characters length was selected arbitrarily as 'long enough'."""
    return "".join(random.choices(_GENERATION_CHARSET, k=length))

def get_execution_dir(*subdirs_to_append: str):
    """Gets the absolute directory where this script or executable is running from.
    This is different from the current process directory, which is obtained from `os.get_cwd()`.
    Additional subdirectories can be appended to the resulting directory."""
    is_exe = getattr(sys, 'frozen', False)
    execution_path = sys.executable if is_exe else sys.argv[0]
    execution_dir = os.path.abspath(os.path.dirname(execution_path))
    return os.path.join(execution_dir, *subdirs_to_append)

def b64_encode(text: str):
    """Encodes a UTF-8 string into its Base-64 representation."""
    return base64.b64encode(text.encode()).decode()

def b64_decode(text: str):
    """Decodes a Base-64 string into its UTF-8 representation."""
    return base64.b64decode(text.encode()).decode()