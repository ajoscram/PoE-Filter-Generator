from typing import Callable
from .generator_error import GeneratorError
from .block import Block
from .filter import Filter

_HANDLER_NOT_FOUND_ERROR = "Handler '{0}' was not found."

class Generator:
    def __init__(self, handlers: dict[str, Callable[[Filter, Block, list[str]], list[str]]]):
        self._handlers = handlers

    def generate(self, filter: Filter, output_filepath: str, handler_name: str, options: list[str]):
        """Imports the module specified by handler_name and gives it a reference to the filter, a Block and a list of option strings.
        The handler must be a python file under the directory "handlers", and the '.py' extension must be omitted.
        The handler must include the function `handle(filter: Filter, block: Block, options: list[str])`."""
        if handler_name not in self._handlers:
            raise GeneratorError(_HANDLER_NOT_FOUND_ERROR.format(handler_name))
        handler = self._handlers[handler_name]
        generated_raw_lines = [ line for block in filter.blocks for line in handler(filter, block, options) ]
        return Filter(output_filepath, Block.extract(generated_raw_lines))