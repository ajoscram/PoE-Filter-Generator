import requests, re, console
from re import MULTILINE, DOTALL

NAME = "help"

_HELP_MESSAGE = "Visit https://github.com/ajoscram/PoE-Filter-Generator/wiki#usage for more information."

def execute(_):
    console.write(_HELP_MESSAGE)

    # response = requests.get("https://raw.githubusercontent.com/wiki/ajoscram/PoE-Filter-Generator/asdas.md")
    # text = re.sub("^\\s*##", "#", response.text, flags=MULTILINE)
    # text = re.sub("```\n([^`]*)```", "```rb\n\\1```", text, flags=DOTALL)