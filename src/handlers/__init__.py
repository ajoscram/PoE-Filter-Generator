"""Contains all handlers used to modify filters and their respective context initializers."""
from typing import Callable
from core import Filter, Block
from .context import Context
from . import econ, format, if_, import_, index, strict, tag, alias, game

CONTEXT_INITIALIZERS: dict[str, Callable[[Filter, list[str]], Context]] = {
    econ.NAME: Context,
    format.NAME: Context,
    import_.NAME: Context,
    index.NAME: index.IndexContext,
    strict.NAME: Context,
    tag.NAME: Context,
    if_.NAME: Context,
    alias.NAME: alias.AliasContext,
    game.NAME: Context,
}

HANDLERS: dict[str, Callable[[Block, Context], list[str]]] = {
    econ.NAME: econ.handle,
    format.NAME: format.handle,
    import_.NAME: import_.handle,
    index.NAME: index.handle,
    strict.NAME: strict.handle,
    tag.NAME: tag.handle,
    if_.NAME: if_.handle,
    alias.NAME: alias.handle,
    game.NAME: game.handle,
}