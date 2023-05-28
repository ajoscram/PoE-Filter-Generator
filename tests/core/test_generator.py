import importlib, pytest
from pytest import MonkeyPatch
from src.core import Filter, Block, generator, GeneratorError

class MockHandler:
    def __init__(self, lines: list[str]):
        self.lines = lines
        self.options_handled = None
        self.filter_handled = None
        self.block_handled = None
        self.handler_path = None
    
    def handle(self, filter: Filter, block: Block, options: list[str]):
        self.options_handled = options
        self.filter_handled = filter
        self.block_handled = block
        return self.lines
    
def test_generate_given_a_handler_is_found_should_generate_a_new_correct_filter(monkeypatch: MonkeyPatch):
    BLOCK = Block.extract([ "line" ])
    FILTER = Filter("", [ BLOCK ])
    HANDLER_NAME = "handler"
    OUTPUT_FILEPATH = "output"
    OPTIONS = [ "option1", "option2" ]
    LINES = [ "line 1", "line 2", "line 3" ]
    mockHandler = _patch_module_and_get_mock_handler(monkeypatch, LINES)

    output_filter = generator.generate(FILTER, OUTPUT_FILEPATH, HANDLER_NAME, OPTIONS)

    assert [ str(line) for line in output_filter.blocks[0].lines ] == LINES
    assert mockHandler.handler_path == generator._HANDLERS_PATH + HANDLER_NAME
    assert mockHandler.filter_handled == FILTER
    assert mockHandler.block_handled == BLOCK
    assert mockHandler.options_handled == OPTIONS
    assert output_filter.filepath == OUTPUT_FILEPATH

def test_generate_given_a_handler_could_not_be_found_should_raise(monkeypatch: MonkeyPatch):
    HANDLER_NAME = "handler"
    ERROR_MESSAGE = generator._HANDLER_NOT_FOUND_ERROR.format(HANDLER_NAME)
    def import_module_raise(_): raise ModuleNotFoundError
    monkeypatch.setattr(importlib, "import_module", import_module_raise)

    with pytest.raises(GeneratorError) as error:
        generator.generate(None, None, HANDLER_NAME, None)
    
    assert error.value.message == ERROR_MESSAGE


def _patch_module_and_get_mock_handler(monkeypatch: MonkeyPatch, expected_lines: list[str]):
    mockHandler = MockHandler(expected_lines)
    def import_module(handler_path: str):
        mockHandler.handler_path = handler_path
        return mockHandler
    monkeypatch.setattr(importlib, "import_module", import_module)
    return mockHandler