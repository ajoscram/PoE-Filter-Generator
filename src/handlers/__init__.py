"""Contains all handlers used to modify filters and their respective context initializers."""
from dataclasses import dataclass
from typing import Callable
from core import Filter, Block
from .context import Context
from . import econ, format, if_, import_, index, strict, tag, alias, game

type ContextInitializer = Callable[[Filter, list[str]], Context]
type HandleFunction = Callable[[Block, Context], list[str]]

@dataclass
class Handler:
    handle: HandleFunction
    initialize_context: ContextInitializer

HANDLERS: dict[str, Handler] = {
    econ.NAME: Handler(econ.handle, Context),
    format.NAME: Handler(format.handle, Context),
    import_.NAME: Handler(import_.handle, import_.ImportContext),
    index.NAME: Handler(index.handle, index.IndexContext),
    strict.NAME: Handler(strict.handle, Context),
    tag.NAME: Handler(tag.handle, Context),
    if_.NAME: Handler(if_.handle, Context),
    alias.NAME: Handler(alias.handle, alias.Context),
    game.NAME: Handler(game.handle, Context),
}