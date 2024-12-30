import os
from .expected_error import ExpectedError
from .block import Block
from .constants import FILE_ENCODING

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

    def save(self, filepath: str):
        """Saves the filter to the filepath received."""
        self._create_directory(filepath)
        block_texts = [ str(block) for block in self.blocks ]
        self._write_filter(filepath, "\n".join(block_texts))

    def _create_directory(self, filepath: str):
        directory = os.path.dirname(filepath)
        if directory != "":
            os.makedirs(directory, exist_ok=True)

    def _write_filter(self, filepath: str, text: str):
        try:
            with open(filepath, "w", encoding=FILE_ENCODING) as file:
                file.write(text)
        except FileExistsError as error:
            raise ExpectedError(_FILE_EXISTS_ERROR, filepath=filepath) from error
        except PermissionError as error:
            raise ExpectedError(_PERMISSION_ERROR, filepath=filepath) from error

def _get_blocks(filepath: str):
    try:
        with open(filepath, "r", encoding=FILE_ENCODING) as file:
            raw_lines = file.readlines()
            return Block.extract(raw_lines)
    except FileNotFoundError as error:
        raise ExpectedError(_FILE_NOT_FOUND_ERROR, filepath=filepath) from error
    except PermissionError as error:
        raise ExpectedError(_PERMISSION_ERROR, filepath=filepath) from error