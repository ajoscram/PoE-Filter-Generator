import random, string, sys, os, base64
from core import Delimiter, ExpectedError

_RANDOM_STR_GENERATION_CHARSET = string.ascii_letters + string.digits

_KVP_MISSING_KEY_ERROR = "The key/value pair '{0}' is missing its key (the text before the equals sign)."
_KVP_MISSING_VALUE_ERROR = "The key/value pair '{0}' is missing its value (the text after the equals sign)."
_KVP_EQUALS_COUNT_ERROR = "The key/value pair '{0}' must contain exactly one equals sign."
_KVP_EMPTY_ERROR = "Encountered an empty key/value pair in '{0}'."
_KVP_EXAMPLE = " Key/value pair lists should look like this:\n\n\tkey1 = value1, key2 = value2, ..."

def get_random_str(length: int = 20):
    """Returns a random string of numbers and upper/lowercase letters of `length` size.
    The default 20 characters length was selected arbitrarily as 'long enough'."""
    return "".join(random.choices(_RANDOM_STR_GENERATION_CHARSET, k=length))

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

def parse_key_value_list(text: str, line_number: int | None = None) -> list[tuple[str, str]]:
    """Returns a list of key/value pairs as tuples extracted from `text`.
    The format must be `key1 = value1, key2 = value2, ...`.
    `line_number` is used to provide better messages should errors be encountered."""
    if text.strip() == "":
        return []
    
    return [ _parse_key_value_pair(pair_text, text, line_number)
        for pair_text in text.split(Delimiter.LIST_ENTRY_SEPARATOR) ]

def _parse_key_value_pair(pair_text: str, source_text: str, line_number: int | None):
    if pair_text.strip() == "":
        raise ExpectedError(_KVP_EMPTY_ERROR.format(source_text) + _KVP_EXAMPLE, line_number)

    parts = pair_text.split(Delimiter.PAIR_SEPARATOR)
    if len(parts) != 2:
        raise ExpectedError(_KVP_EQUALS_COUNT_ERROR.format(pair_text) + _KVP_EXAMPLE, line_number)
    
    key = parts[0].strip()
    if key == "":
        raise ExpectedError(_KVP_MISSING_KEY_ERROR.format(pair_text) + _KVP_EXAMPLE, line_number)

    value = parts[1].strip()
    if value == "":
        raise ExpectedError(_KVP_MISSING_VALUE_ERROR.format(pair_text) + _KVP_EXAMPLE, line_number)
    
    return key, value