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
    return list(_get_raw_lines_from_block(block, context))

def _get_initial_import(filepath: str, block: Block):
    name_rules = block.get_rules(RuleName.NAME)
    blockname = name_rules[-1].description.strip() \
        if len(name_rules) > 0 else None
    return Import(filepath, blockname)

def _get_raw_lines_from_filter(filter: Filter, context: ImportContext) -> Generator[str, None, None]:
    return (raw_line
        for block in filter.blocks
        for raw_line in _get_raw_lines_from_block(block, context))

def _get_raw_lines_from_block(block: Block, context: ImportContext, include_blockstarts: bool = True) -> Generator[str, None, None]:
    return (raw_line
        for block_line in block.lines
        for raw_line in _get_raw_lines_from_line(block_line, context, include_blockstarts))

def _get_raw_lines_from_line(line: Line, context: ImportContext, include_blockstarts: bool) -> Generator[str, None, None]:
    if include_blockstarts or not line.is_block_starter():
        yield _get_raw_line(line, context)

    for rule in line.get_rules(RuleName.IMPORT):
        for line in _get_raw_lines_from_rule(rule, context):
            yield _get_raw_line(line, context)

def _get_raw_lines_from_rule(rule: Rule, context: ImportContext) -> Generator[str, None, None]:
    new_import = parse.extract(rule, context)

    filter = _get_filter(new_import.filepath, context)
    if new_import.blockname is None:
        return _get_raw_lines_from_filter(filter, context.clone(new_import))

    block = _get_block(filter, new_import.blockname)
    return _get_raw_lines_from_block(block, context.clone(new_import), include_blockstarts=False)

def _get_raw_line(line: Line, context: ImportContext):
    raw_line = str(line)
    for template_name, replacement_text in context.templates.items():
        raw_line = raw_line.replace(template_name, replacement_text)
    return raw_line

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