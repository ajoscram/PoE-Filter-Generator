"""Contains all handlers used to modify filters."""
from typing import Callable
from core import Filter, Block
from . import econ, format, if_, import_, index, strict, tag, alias, game

HANDLERS: dict[str, Callable[[Filter, Block, list[str]], list[str]]] = {
    econ.NAME: econ.handle,
    format.NAME: format.handle,
    import_.NAME: import_.handle,
    index.NAME: index.handle,
    strict.NAME: strict.handle,
    tag.NAME: tag.handle,
    if_.NAME: if_.handle,
    alias.NAME: alias.handle,
    game.NAME: game.handle
}