from core import ExpectedError
from rich.console import Console
from rich.markdown import Markdown

_DONE_MESSAGE = "[green]Done![/]"
_EXPECTED_ERROR_TEMPLATE = "[red]ERROR[/]: {0}"
_UNKNOWN_ERROR_MESSAGE = """[red]UNKNOWN ERROR[/]: Oopsie, my bad.

If your're reading this then an unforseen error has ocurred.
I'd greatly appreciate if you could submit an issue on Github:

https://github.com/ajoscram/PoE-Filter-Generator/issues/new

With the following text (or a screenshot of it):"""

_CONSOLE = Console()

def write(*values, markdown: bool = False, done: bool = False):
    """Writes the values passed in to the stdout, with formatting depending on the object.
        - If `markdown` is `True` the text is formatted as markdown.
        - If `done` is `True`, then a green "Done!" message is prepended to the values.
    """
    if markdown:
        values = (_create_markdown(*values), )
    if done:
        values = (_DONE_MESSAGE, ) + values

    _CONSOLE.print(*values, end="\n\n")

def err(exception: Exception):
    """Prints the `exception` passed in.
    If `exception` is NOT an `ExpectedError` then a preamble is printed
    alongside the `exception`'s traceback and message.
    """
    if isinstance(exception, ExpectedError):
        return write(_EXPECTED_ERROR_TEMPLATE.format(exception))
    
    write(_UNKNOWN_ERROR_MESSAGE)
    _CONSOLE.print_exception(show_locals=True)

def _create_markdown(*values):
    text = "".join(str(value) for value in values)
    return Markdown(text)