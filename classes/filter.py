import os

from classes.generator_error import GeneratorError
from .block import Block

_FILE_EXISTS_ERROR = "The file path corresponds to an already existing file"
_FILE_NOT_FOUND_ERROR = "The input file was not found"
_PERMISSION_ERROR = "You don't have permission to read or write on this directory or file"

class Filter:
    """The filter class is a representation of a .filter file."""

    def __init__(self, filepath: str, blocks: list[Block] = None):
        self.filepath: str = filepath
        self.blocks: list[Block] = blocks if blocks != None else self._get_blocks(filepath)

    def _get_blocks(self, filepath: str):
        try:
            with open(self.filepath, "r") as file:
                raw_lines = file.readlines()
                return Block.extract(raw_lines)
        except FileNotFoundError:
            raise GeneratorError(_FILE_NOT_FOUND_ERROR, filepath=filepath)
        except PermissionError:
            raise GeneratorError(_PERMISSION_ERROR, filepath=filepath)

    def save(self, output_filepath: str):
        """Saves the filter to the indicated output filepath."""
        self._create_directory(output_filepath)
        try:
            text = ""
            for block in self.blocks:
                text_to_merge = [ text ] if text != "" else []
                text = "\n".join(text_to_merge + [ line.text for line in block.lines ])
            with open(output_filepath, "w") as file:
                file.write(text)
        except FileExistsError:
            raise GeneratorError(_FILE_EXISTS_ERROR, filepath=self.filepath)
        except PermissionError:
            raise GeneratorError(_PERMISSION_ERROR, filepath=self.filepath)
    
    def _create_directory(self, filepath: str):
        directory = os.path.dirname(filepath)
        if directory != "":
            os.makedirs(directory, exist_ok=True)
    
    def __str__(self):
        string = f"Filter @ {self.filepath}"
        for block in self.blocks:
            string += f"\n\n{block}"
        return string