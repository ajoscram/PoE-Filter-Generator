import os.path

import classes.block
from common import util
from classes.filter import Filter
from classes.generator_error import GeneratorError
from classes.rule import Rule
from classes.block import Block

_NAME = "append"
_SPLITTER = "->"
_BLOCK_NAME = "name"

_INCORRECT_RULE_FORMAT_ERROR = "The {0} '{1}' is formatted incorrectly. Make sure your append rules look like this:\n\n\tfile > path > to > filter -> block_name"
_EMPTY_BLOCK_NAME_ERROR = "The {0} '{1}' has no block name. Make sure to provide one after the arrow."
_BLOCK_NOT_FOUND_ERROR = "The block with name '{0}' was not found."

_filter_cache: dict[str, Filter] = {}

def handle(filter: Filter, block: Block, _):
    """Handles appends of lines to blocks. Options are ignored."""
    new_block = Block(block.line_number)
    params = _get_initial_params(filter.filepath, block)
    for line in _get_lines(block, filter.filepath, params):
        new_block.append(line)
    return [ new_block ]

def _get_initial_params(filepath: str, block: Block):
    name_rules = block.get_rules(_BLOCK_NAME)
    if len(name_rules) > 0:
        return [ { "filepath": filepath, "block_name": name_rules[-1].description } ]
    else:
        return []

def _get_lines(block: Block, filepath: str, previous_params: list[dict[str, str]]):
    lines = []
    line_index = 0
    for rule in block.get_rules(_NAME):
        lines_to_append = _get_lines_to_append(rule, filepath, previous_params)
        lines += block.lines[line_index : rule.line_number - block.line_number + 1]
        lines += [ line for line in lines_to_append if _line_is_valid(line) ]
        line_index = rule.line_number - block.line_number + 1
    return lines + block.lines[line_index :]

def _get_lines_to_append(rule: Rule, filepath: str, previous_params: list[dict[str, str]]):
    params = _parse_rule_params(rule, filepath, previous_params)
    append_filter = _get_filter(params["filepath"])
    append_block = _get_block(append_filter, params["block_name"])
    return _get_lines(append_block, append_filter.filepath, previous_params + [ params ])

def _parse_rule_params(rule: Rule, current_filepath: str, previous_params: list[dict[str, str]]):
    parts = rule.description.split(_SPLITTER)
    if len(parts) != 2:
        util.raise_rule_error(_INCORRECT_RULE_FORMAT_ERROR, current_filepath, rule)
    
    filepath = util.parse_rule_filepath(current_filepath, parts[0].strip())
    if not os.path.exists(filepath):
        util.raise_rule_error(util.DOES_NOT_EXIST_ERROR, current_filepath, rule)

    block_name = parts[1].strip()
    if block_name == "":
        util.raise_rule_error(_EMPTY_BLOCK_NAME_ERROR, current_filepath, rule)
    
    params = { "filepath": filepath, "block_name": block_name }
    if any(_are_params_equal(params, previous) for previous in previous_params):
        util.raise_rule_error(util.CIRCULAR_REFERENCE_ERROR, current_filepath, rule)

    return params

def _get_filter(filepath: str):
    absolute_filepath = os.path.abspath(filepath)

    if absolute_filepath not in _filter_cache:
        _filter_cache[absolute_filepath] = Filter(filepath)

    return _filter_cache[absolute_filepath]

def _get_block(filter: Filter, block_name: str):
    for block in filter.blocks:
        for rule in block.get_rules(_BLOCK_NAME):
            if rule.description == block_name:
                return block
    raise GeneratorError(_BLOCK_NOT_FOUND_ERROR.format(block_name), filepath=filter.filepath)

def _line_is_valid(line: str):
    show_start = line.lstrip().startswith(classes.block._SHOW)
    hide_start = line.lstrip().startswith(classes.block._HIDE)
    return not show_start and not hide_start

def _are_params_equal(first: dict[str, str], second: dict[str, str]):
    same_filter = os.path.samefile(first["filepath"], second["filepath"])
    same_block = first["block_name"] == second["block_name"]
    return same_filter and same_block