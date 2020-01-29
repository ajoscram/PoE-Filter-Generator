"""Module that exports the Generator class only."""
import importlib
from .section import Section

class Generator:
    """The generator is a mediator class that invokes handlers with the filter data.
    The sectionize function reads a file and returns a list of Section objects found in that file.
    The generate function loads a module with the 'handler' name and calls a function 'handle' on it. It is up to the handler any processing required."""

    SHOW = "Show"
    HIDE = "Hide"
    HANDLERS_PATH = "handlers."

    def sectionize(self, filepath: str):
        """Returns the sections in a filter file located at filepath, split at every "Show" or "Hide". Filepath must exist and be readable."""
        try:
            file = open(filepath, "r")
            lines = file.readlines()
            sections = []
            line_count = 1
            current = Section(line_count)
            for line in lines:
                #check if the line starts with show or hide, if so start a new section
                line_stripped = line.lstrip()
                if line_stripped.startswith(self.SHOW) or line_stripped.startswith(self.HIDE):
                    if not current.is_empty():
                        sections.append(current)
                    current = Section(line_count)
                current.append(line.rstrip())
                line_count +=1
            #this is the last section in the file and is omitted in the loop
            if not current.is_empty():
                sections.append(current)
            file.close()
            return sections
        except FileNotFoundError:
            raise GeneratorError(filepath, GeneratorError.FILE_NOT_FOUND)
        except PermissionError:
            raise GeneratorError(filepath, GeneratorError.PERMISSION)

    def generate(self, filepath:str, sections: list, handler: str, options: list = []):
        """Imports the module specified by handler and gives it a list of sections, a filepath to output its result and a list of option strings. The rest is up to the handler.
        The filepath must be writable.
        The handler must be a python file under the directory "handlers", and the '.py' extension must be omitted.
        The handler must include the function handle(filepath:str, sections: list, options:list = [])."""
        try:
            handler = importlib.import_module(self.HANDLERS_PATH + handler)
            handler.handle(filepath, sections, options)
        except ModuleNotFoundError:
            raise GeneratorError(self.HANDLERS_PATH + handler, GeneratorError.HANDLER_NOT_FOUND)
        except PermissionError:
            raise GeneratorError(filepath, GeneratorError.PERMISSION)

class GeneratorError(Exception):
    """Class for generator exception handling."""

    #Error message constants
    HANDLER_NOT_FOUND = "Handler file not found (it must be under the 'handlers' directory)"
    FILE_NOT_FOUND = "The input file was not found"
    PERMISSION = "You don't have permission to read or write on this directory or file"

    def __init__(self, filepath:str, message: str):
        """Takes a source filepath where the error ocurred and a message from the caller."""
        self.message = message
        self.filepath = filepath