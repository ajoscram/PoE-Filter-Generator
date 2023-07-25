import traceback, re
from core import ExpectedError, DEFAULT_WIKI_PAGE_NAME as _DEFAULT_HINT_TERM, COMMAND_START, HANDLER_START
from rich.console import Console
from rich.markdown import Markdown

_DONE_MESSAGE = "[green]Done![/]"
_EXPECTED_ERROR_TEMPLATE = "[red]ERROR[/]: {0}"
_HINT_MESSAGE = "Run [cyan]pfg -help {0}[/] or visit {1} for more information."
_UNKNOWN_ERROR_MESSAGE = """[red]UNKNOWN ERROR[/]: Oopsie, my bad.

If your're reading this then an unforseen error has ocurred.
I'd greatly appreciate if you could submit an issue on Github:

https://github.com/ajoscram/PoE-Filter-Generator/issues/new

With the following text (or a screenshot of it):"""

_HANDLERS_FOLDER_NAME = "handlers"
_COMMANDS_FOLDER_NAME = "commands"
_FILENAME_REGEX = r"\\([^\.]+)\.py"
_HANDLER_FILENAME_REGEX = _HANDLERS_FOLDER_NAME + _FILENAME_REGEX
_COMMAND_FILENAME_REGEX = _COMMANDS_FOLDER_NAME + _FILENAME_REGEX
_WIKI_PAGE_URL = "https://github.com/ajoscram/PoE-Filter-Generator/wiki/{0}"

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
    if not isinstance(exception, ExpectedError):
        write(_UNKNOWN_ERROR_MESSAGE)
        return _CONSOLE.print_exception(show_locals=True)
    
    write(_EXPECTED_ERROR_TEMPLATE.format(exception))
    write(_create_hint(exception))

def _create_markdown(*values):
    text = "".join(str(value) for value in values)
    return Markdown(text)

def _create_hint(error: ExpectedError):
    term = _get_hint_term(error)
    hint_url = _WIKI_PAGE_URL.format(term)
    return _HINT_MESSAGE.format(term, hint_url)

def _get_hint_term(error: ExpectedError):
    reversed_traceback = reversed(traceback.extract_tb(error.__traceback__))
    filepath_trace = [ trace.filename for trace in reversed_traceback ]
    for filepath in filepath_trace:
        handler_filename = _try_get_filename(filepath, _HANDLER_FILENAME_REGEX)
        if handler_filename != None:
            return HANDLER_START + handler_filename
        command_filename = _try_get_filename(filepath, _COMMAND_FILENAME_REGEX)
        if command_filename != None:
            return COMMAND_START + command_filename
    return _DEFAULT_HINT_TERM

def _try_get_filename(filepath: str, pattern: str):
    match = re.search(pattern, filepath)
    if match == None:
        return None
    return match.groups()[0]