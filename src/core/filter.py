import os

from .generator_error import GeneratorError
from .block import Block

_FILE_EXISTS_ERROR = "The file path corresponds to an already existing file"
_FILE_NOT_FOUND_ERROR = "The input file was not found"
_PERMISSION_ERROR = "You don't have permission to read or write on this directory or file"

class Filter:
    """The filter class is a representation of a .filter file."""

    def __init__(self, filepath: str, blocks: list[Block]):
        self.filepath: str = filepath
        self.blocks: list[Block] = blocks

    @classmethod
    def load(cls, filepath: str):
        blocks = cls._get_blocks(filepath)
        return Filter(filepath, blocks)

    @classmethod
    def _get_blocks(cls, filepath: str):
        try:
            with open(filepath, "r") as file:
                raw_lines = file.readlines()
                return Block.extract(raw_lines)
        except FileNotFoundError:
            raise GeneratorError(_FILE_NOT_FOUND_ERROR, filepath=filepath)
        except PermissionError:
            raise GeneratorError(_PERMISSION_ERROR, filepath=filepath)

    def save(self):
        """Saves the filter to its filepath."""
        self._create_directory()
        try:
            block_texts = [ "\n".join(block.get_raw_lines()) for block in self.blocks ]
            text = "\n".join(block_texts)
            with open(self.filepath, "w") as file:
                file.write(text)
        except FileExistsError:
            raise GeneratorError(_FILE_EXISTS_ERROR, filepath=self.filepath)
        except PermissionError:
            raise GeneratorError(_PERMISSION_ERROR, filepath=self.filepath)
    
    def _create_directory(self):
        directory = os.path.dirname(self.filepath)
        if directory != "":
            os.makedirs(directory, exist_ok=True)
    
    def __str__(self):
        string = f"Filter @ {self.filepath}"
        for block in self.blocks:
            string += f"\n\n{block}"
        return string