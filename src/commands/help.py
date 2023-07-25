import re, console, web
from re import MULTILINE, DOTALL
from core import ExpectedError, DEFAULT_WIKI_PAGE_NAME

NAME = "help"

_HTTP_NOT_FOUND_CODE = 404
_MARKDOWN_HEADER = "# {0}\n"
_API_URL = "https://raw.githubusercontent.com/wiki/ajoscram/PoE-Filter-Generator/{0}.md"

_NOT_FOUND_ERROR = "Could not find help information available for '{0}'."
_TOO_MANY_ARGS_ERROR = "The -help command accepts only one argument. You've provided {0}."

def execute(_, args: list[str]):
    search_term = _get_search_term(args)
    text = _get_text(search_term)
    console.write(text, markdown=True)

def _get_search_term(args: list[str]):
    arg_count = len(args)
    if arg_count == 0:
        return DEFAULT_WIKI_PAGE_NAME
    if arg_count > 1:
        raise ExpectedError(_TOO_MANY_ARGS_ERROR.format(arg_count))
    return args[0].lower().capitalize()

def _get_text(term: str):
    custom_errors = { _HTTP_NOT_FOUND_CODE: _NOT_FOUND_ERROR.format(term) }
    markdown_text = web.get(_API_URL.format(term), json=False, custom_http_errors=custom_errors)
    return _format_markdown(markdown_text, term)
    
def _format_markdown(text: str, header: str):
    text = re.sub("^\\s*##", "#", text, flags=MULTILINE)
    text = re.sub("```\n([^`]*)```", "```rb\n\\1```", text, flags=DOTALL)
    return _MARKDOWN_HEADER.format(header) + text