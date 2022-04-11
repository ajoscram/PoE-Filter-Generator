import os

from classes.generator_error import GeneratorError
from .section import Section

_FILE_EXISTS_ERROR = "The file path corresponds to an already existing file"
_FILE_NOT_FOUND_ERROR = "The input file was not found"
_PERMISSION_ERROR = "You don't have permission to read or write on this directory or file"

class Filter:
    """The filter class is a representation of a .filter file."""

    def __init__(self, filepath: str, sections: list[Section] = None):
        self.filepath: str = filepath
        self.sections: list[Section] = sections or self._get_sections(filepath)

    def _get_sections(self, filepath: str):
        try:
            with open(self.filepath, "r") as file:
                lines = file.readlines()
                return Section.extract(lines)
        except FileNotFoundError:
            raise GeneratorError(_FILE_NOT_FOUND_ERROR, filepath=filepath)
        except PermissionError:
            raise GeneratorError(_PERMISSION_ERROR, filepath=filepath)

    def save(self, output_filepath: str):
        """Saves the filter to the indicated output filepath."""
        self._create_directory(output_filepath)
        try:
            with open(output_filepath, "w") as file:
                for section in self.sections:
                    for line in section.lines:
                        file.write(line + '\n')
        except FileExistsError:
            raise GeneratorError(_FILE_EXISTS_ERROR, filepath=self.filepath)
        except PermissionError:
            raise GeneratorError(_PERMISSION_ERROR, filepath=self.filepath)
    
    def _create_directory(self, filepath: str):
        directory = os.path.dirname(filepath)
        if directory != "":
            os.makedirs(directory, exist_ok=True)