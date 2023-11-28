import os

from .expected_error import ExpectedError
from .block import Block

_FILE_EXISTS_ERROR = "The file path corresponds to an already existing file"
_FILE_NOT_FOUND_ERROR = "The input file was not found"
_PERMISSION_ERROR = "You don't have permission to read or write on this directory or file"

class Filter:
    """The Filter class is a representation of a .filter file."""
    def __init__(self, filepath: str, blocks: list[Block]):
        self.filepath: str = filepath
        self.blocks: list[Block] = blocks

    @classmethod
    def load(cls, filepath: str):
        """Creates a new Filter objects from a `.filter` file."""
        blocks = _get_blocks(filepath)
        return Filter(filepath, blocks)

    def save(self):
        """Saves the filter to its filepath."""
        self._create_directory()
        block_texts = [ str(block) for block in self.blocks ]
        self._write_filter("\n".join(block_texts))

    def _create_directory(self):
        directory = os.path.dirname(self.filepath)
        if directory != "":
            os.makedirs(directory, exist_ok=True)
    
    def _write_filter(self, text: str):
        try:
            with open(self.filepath, "w") as file:
                file.write(text)
        except FileExistsError:
            raise ExpectedError(_FILE_EXISTS_ERROR, filepath=self.filepath)
        except PermissionError:
            raise ExpectedError(_PERMISSION_ERROR, filepath=self.filepath)

def _get_blocks(filepath: str):
    try:
        with open(filepath, "r") as file:
            raw_lines = file.readlines()
            return Block.extract(raw_lines)
    except FileNotFoundError:
        raise ExpectedError(_FILE_NOT_FOUND_ERROR, filepath=filepath)
    except PermissionError:
        raise ExpectedError(_PERMISSION_ERROR, filepath=filepath)