from typing import Callable
from core import Filter, Block
from . import choose, econ, format, import_, index, strict, tag

HANDLERS: dict[str, Callable[[Filter, Block, list[str]], list[str]]] = {
    choose.NAME: choose.handle,
    econ.NAME: econ.handle,
    format.NAME: format.handle,
    import_.NAME: import_.handle,
    index.NAME: index.handle,
    strict.NAME: strict.handle,
    tag.NAME: tag.handle,
}