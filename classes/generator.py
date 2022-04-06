import importlib

from classes.generator_error import GeneratorError
from .filter import Filter

class Generator:
    """The generator is a mediator class that invokes handlers with the filter data.
    The generate function loads a module with the 'handler' name and calls a function 'handle' on it. It is up to the handler any processing required."""

    HANDLERS_PATH = "handlers."
    HANDLER_NOT_FOUND_ERROR = "Handler '{0}' was not found."

    def generate(self, filter: Filter, handler_name: str, options: list[str]):
        """Imports the module specified by handler and gives it a list of sections, a filepath to output its result and a list of option strings. The rest is up to the handler.
        The filepath must be writable.
        The handler must be a python file under the directory "handlers", and the '.py' extension must be omitted.
        The handler must include the function handle(filter: Filter, section: Section, options: list[str])."""
        handler = self.__get_handler__(handler_name)
        new_sections = []
        for section in filter.sections:
            new_sections += handler.handle(filter, section, options)
        return Filter(filter.filepath, new_sections)

    def __get_handler__(self, handler_name: str):
        try:
            return importlib.import_module(Generator.HANDLERS_PATH + handler_name)
        except ModuleNotFoundError:
            raise GeneratorError(Generator.HANDLER_NOT_FOUND_ERROR.format(handler_name))