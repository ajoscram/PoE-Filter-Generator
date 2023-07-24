import re, console, web
from re import MULTILINE, DOTALL

NAME = "help"

_SHORT = "short"
_USAGE_PAGE_NAME = "Usage"
_SHORT_MESSAGE = "Visit {0} for more information."
_MARKDOWN_HEADER = "# {0}\n"

_API_URL = "https://raw.githubusercontent.com/wiki/ajoscram/PoE-Filter-Generator/{0}.md"
_WEB_PAGE_URL = "https://github.com/ajoscram/PoE-Filter-Generator/wiki/{0}"

_NOT_FOUND_ERROR = "Could not find help information available for '{0}'."
_HTTP_NOT_FOUND_CODE = 404

class _Params:
    def __init__(self, term: str, is_markdown: bool):
        self.term = term
        self.is_markdown = is_markdown

def execute(_, options: list[str]):
    params = _get_params(options)
    text = _get_text(params)
    console.write(text, markdown=params.is_markdown)

def _get_params(options: list[str]):
    options = [ option.lower() for option in options ]
    if len(options) == 0 or options[0] == _SHORT:
        options = [ _USAGE_PAGE_NAME ] + options
    
    query = options[0].capitalize()
    is_markdown = _SHORT not in options
    return _Params(query, is_markdown)

def _get_text(params: _Params):
    custom_errors = { _HTTP_NOT_FOUND_CODE: _NOT_FOUND_ERROR.format(params.term) }
    markdown_text = web.get(_API_URL.format(params.term), json=False, custom_http_errors=custom_errors)

    if params.is_markdown:
        return _format_markdown(markdown_text, params.term)

    web_page_url = _WEB_PAGE_URL.format(params.term)
    return _SHORT_MESSAGE.format(web_page_url)

def _format_markdown(text: str, header: str):
    text = re.sub("^\\s*##", "#", text, flags=MULTILINE)
    text = re.sub("```\n([^`]*)```", "```rb\n\\1```", text, flags=DOTALL)
    return _MARKDOWN_HEADER.format(header) + text