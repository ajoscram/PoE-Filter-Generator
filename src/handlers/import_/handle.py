import os
from typing import Generator
from core import Filter, Block, Line, Rule, ExpectedError
from .import_context import ImportContext
from .import_ import Import
from .constants import RuleName
from . import parse

_BLOCK_NOT_FOUND_ERROR = "The block with name '{0}' was not found."

def handle(block: Block, context: ImportContext):
    """Handles text import from filter files.
    Absolute paths can be defined via the options."""
    initial_import = _get_initial_import(context.filter.filepath, block)
    context = context.clone(initial_import)
    return [ str(line) for line in _get_lines_from_block(block, context, True) ]

def _get_initial_import(filepath: str, block: Block):
    name_rules = block.get_rules(RuleName.NAME)
    blockname = name_rules[-1].description.strip() \
        if len(name_rules) > 0 else None
    return Import(filepath, blockname)

def _get_lines_from_filter(filter: Filter, context: ImportContext) -> Generator[Line, None, None]:
    return (line
        for block in filter.blocks
        for line in _get_lines_from_block(block, context, True))

def _get_lines_from_block(block: Block, context: ImportContext, include_blockstarts: bool) -> Generator[Line, None, None]:
    return (line
        for block_line in block.lines
        for line in _get_lines_from_line(block_line, context, include_blockstarts))

def _get_lines_from_line(line: Line, context: ImportContext, include_blockstarts: bool) -> Generator[Line, None, None]:
    if include_blockstarts or not line.is_block_starter():
        yield line # TODO: account for templating

    for rule in line.get_rules(RuleName.IMPORT):
        for line in _get_lines_from_rule(rule, context):
            yield line

def _get_lines_from_rule(rule: Rule, context: ImportContext) -> Generator[Line, None, None]:
    new_import = parse.extract(rule, context)

    filter = _get_filter(new_import.filepath, context)
    if new_import.blockname is None:
        return _get_lines_from_filter(filter, context.clone(new_import))

    block = _get_block(filter, new_import.blockname)
    return _get_lines_from_block(block, context.clone(new_import), False)

def _get_filter(filepath: str, context: ImportContext):
    absolute_filepath = os.path.abspath(filepath)

    if absolute_filepath not in context.cache:
        context.cache[absolute_filepath] = Filter.load(filepath)

    return context.cache[absolute_filepath]

def _get_block(filter: Filter, blockname: str):
    for block in filter.blocks:
        if blockname == _get_blockname(block):
            return block
    error = _BLOCK_NOT_FOUND_ERROR.format(blockname)
    raise ExpectedError(error, filepath=filter.filepath)

def _get_blockname(block: Block):
    name_rules = block.get_rules(RuleName.NAME)
    return name_rules[-1].description if len(name_rules) > 0 else None