from typing import Callable
from . import help, generate, update, path, clean
from .generate import NAME as DEFAULT_COMMAND_NAME

COMMANDS: dict[str, Callable[[str, list[str]], None]] = {
    generate.NAME: generate.execute,
    help.NAME: help.execute,
    update.NAME: update.execute,
    path.NAME: path.execute,
    clean.NAME: clean.execute,
}