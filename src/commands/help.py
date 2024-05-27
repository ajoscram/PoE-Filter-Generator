import re, console, web
from re import MULTILINE, DOTALL
from core import ExpectedError, DEFAULT_WIKI_PAGE_NAME, COMMAND_START

NAME = "help"

_HTTP_NOT_FOUND_CODE = 404
_MARKDOWN_HEADER = "# {0}\n"
_SIDEBAR_PAGE_NAME = "_Sidebar"
_API_URL = "https://raw.githubusercontent.com/wiki/ajoscram/PoE-Filter-Generator/{0}.md"

_NOT_FOUND_ERROR = "Could not find help information available for '{0}'."
_TOO_MANY_ARGS_ERROR = "The " + COMMAND_START + NAME + " command accepts only one argument. You've provided {0}."

def execute(args: list[str]):
    """Performs a PFG Documentation search for a term specified in the `args`."""
    search_term = _get_search_term(args)
    text = _get_text(search_term)

    if search_term == DEFAULT_WIKI_PAGE_NAME:
        text += _get_help_terms()
    
    console.write(text, markdown=True)

def _get_search_term(args: list[str]):
    arg_count = len(args)
    if arg_count == 0:
        return DEFAULT_WIKI_PAGE_NAME
    if arg_count > 1:
        raise ExpectedError(_TOO_MANY_ARGS_ERROR.format(arg_count))
    return args[0].lower().capitalize()

def _get_text(term: str):
    return web.get(
        _API_URL.format(term),
        web.Expiration.DAILY,
        formatter = lambda x: _format_markdown(x, term),
        custom_http_errors = { _HTTP_NOT_FOUND_CODE: _NOT_FOUND_ERROR.format(term) })

def _get_help_terms():
    text = _get_text(_SIDEBAR_PAGE_NAME)
    header = _MARKDOWN_HEADER.format(_SIDEBAR_PAGE_NAME)
    return "\n" + text.removeprefix(header)

def _format_markdown(text: str, header: str):
    text = re.sub("^\\s*##", "#", text, flags=MULTILINE)
    text = re.sub("```\n([^`]*)```", "```rb\n\\1```", text, flags=DOTALL)
    return _MARKDOWN_HEADER.format(header) + text