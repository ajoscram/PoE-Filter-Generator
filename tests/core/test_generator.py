import pytest
from core import Filter, Block, Generator, GeneratorError
from core.generator import _HANDLER_NOT_FOUND_ERROR

HANDLER_NAME = "handler"
class MockHandler:
    def __init__(self, lines: list[str]):
        self.lines = lines
        self.options_handled = None
        self.filter_handled = None
        self.block_handled = None
    
    def handle(self, filter: Filter, block: Block, options: list[str]):
        self.options_handled = options
        self.filter_handled = filter
        self.block_handled = block
        return self.lines

def test_generate_given_a_handler_is_found_should_generate_a_new_correct_filter():
    BLOCK = Block.extract([ "line" ])
    FILTER = Filter("", [ BLOCK ])
    OUTPUT_FILEPATH = "output"
    OPTIONS = [ "option1", "option2" ]
    LINES = [ "line 1", "line 2", "line 3" ]
    mock_handler, handler_dict = _get_mock_handler_and_dict(LINES)
    generator = Generator(handler_dict)

    output_filter = generator.generate(FILTER, OUTPUT_FILEPATH, HANDLER_NAME, OPTIONS)

    assert [ str(line) for line in output_filter.blocks[0].lines ] == LINES
    assert mock_handler.filter_handled == FILTER
    assert mock_handler.block_handled == BLOCK
    assert mock_handler.options_handled == OPTIONS
    assert output_filter.filepath == OUTPUT_FILEPATH

def test_generate_given_a_handler_could_not_be_found_should_raise():
    ERROR_MESSAGE = _HANDLER_NOT_FOUND_ERROR.format(HANDLER_NAME)
    generator = Generator({})

    with pytest.raises(GeneratorError) as error:
        generator.generate(None, None, HANDLER_NAME, None)
    
    assert error.value.message == ERROR_MESSAGE

def _get_mock_handler_and_dict(expected_lines: list[str]):
    mock_handler = MockHandler(expected_lines)
    handler_dict = { HANDLER_NAME: mock_handler.handle }
    return (mock_handler, handler_dict)