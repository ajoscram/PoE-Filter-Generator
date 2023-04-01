import importlib

from .generator_error import GeneratorError
from .block import Block
from .filter import Filter

_HANDLERS_PATH = "src.handlers."
_HANDLER_NOT_FOUND_ERROR = "Handler '{0}' was not found."

class Generator:
    """The generator is a mediator class that invokes handlers with the filter data.
    The generate function loads a module with the 'handler' name and calls a function 'handle' on it.
    Any processing required is up to the handler."""

    def generate(self, filter: Filter, output_filepath: str, handler_name: str, options: list[str]):
        """Imports the module specified by handler_name and gives it a reference to the filter, a Block and a list of option strings.
        The handler must be a python file under the directory "handlers", and the '.py' extension must be omitted.
        The handler must include the function handle(filter: Filter, block: Block, options: list[str])."""
        handler = self._get_handler(handler_name)
        generated_raw_lines = []
        for block in filter.blocks:
            generated_raw_lines += handler.handle(filter, block, options)
        return Filter(output_filepath, Block.extract(generated_raw_lines))

    def _get_handler(self, handler_name: str):
        try:
            return importlib.import_module(_HANDLERS_PATH + handler_name)
        except ModuleNotFoundError:
            raise GeneratorError(_HANDLER_NOT_FOUND_ERROR.format(handler_name))