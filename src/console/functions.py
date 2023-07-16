import traceback
from core import ExpectedError
from commands import help

_EXPECTED_ERROR_TEMPLATE = "ERROR: {0}"
_EXCEPTION_TEMPLATE = "\n{0}: {1}"
_UNKNOWN_ERROR_MESSAGE = """UNKNOWN ERROR: Oopsie, my bad

If your're reading this then an unforseen error has ocurred. Notify me immediately so I can fix it!
Please provide either the following text from the error or a screenshot via an issue on GitHub:

https://github.com/ajoscram/PoE-Filter-Generator/issues/new

Thanks!"""

# md = Markdown(text)
# console = Console()
# console.print(md)

# https://rich.readthedocs.io/en/stable/markdown.html

def write(*values, markdown = False):
    print(*values)

def err(exception: Exception):
    if isinstance(exception, ExpectedError):
        write(_EXPECTED_ERROR_TEMPLATE.format(exception), '\n')
        return help.execute(None)
    
    write(_UNKNOWN_ERROR_MESSAGE, '\n')
    traceback.print_tb(exception.__traceback__)
    write(_EXCEPTION_TEMPLATE.format(type(exception).__name__, exception))