"""Contains all commands that can be executed by this tool."""
from typing import Callable
from . import help, generate, update, path, clean, watch, publish
from .generate import NAME as DEFAULT_COMMAND_NAME

type Command = Callable[[str, list[str]], None]

COMMANDS: dict[str, Command] = {
    generate.NAME: generate.execute,
    help.NAME: help.execute,
    update.NAME: update.execute,
    path.NAME: path.execute,
    clean.NAME: clean.execute,
    watch.NAME: watch.execute,
    publish.NAME: publish.execute,
}