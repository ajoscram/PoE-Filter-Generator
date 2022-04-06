import os

from classes.generator_error import GeneratorError
from .section import Section

class Filter:
    """The filter class is a representation of a .filter file."""

    FILE_EXISTS_ERROR = "The file path corresponds to an already existing file"
    FILE_NOT_FOUND_ERROR = "The input file was not found"
    PERMISSION_ERROR = "You don't have permission to read or write on this directory or file"

    def __init__(self, filepath: str, sections: list[Section] = None):
        self.filepath: str = filepath
        self.sections: list[Section] = sections or self.__get_sections__(filepath)

    def __get_sections__(self, filepath: str):
        try:
            with open(self.filepath, "r") as file:
                lines = file.readlines()
                return Section.extract(lines)
        except FileNotFoundError:
            raise GeneratorError(Filter.FILE_NOT_FOUND_ERROR, filepath=filepath)
        except PermissionError:
            raise GeneratorError(Filter.PERMISSION_ERROR, filepath=filepath)

    def save(self):
        """Saves the filter to a file located on it's filepath."""
        self.__create_directory__(self.filepath)
        try:
            with open(self.filepath, "w") as file:
                for section in self.sections:
                    for line in section.lines:
                        file.write(line + '\n')
        except FileExistsError:
            raise GeneratorError(Filter.FILE_EXISTS_ERROR, filepath=self.filepath)
        except PermissionError:
            raise GeneratorError(Filter.PERMISSION_ERROR, filepath=self.filepath)
    
    def __create_directory__(self, filepath: str):
        directory = os.path.dirname(filepath)
        if directory != "":
            os.makedirs(directory, exist_ok=True)