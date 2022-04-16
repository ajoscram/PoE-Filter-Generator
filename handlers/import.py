import os.path

from classes.filter import Filter
from classes.rule import Rule
from classes.block import Block
from common import util

_NAME = "import"

def handle(filter: Filter, block: Block, _):
    """Handles imports of other filter files' blocks. Options are ignored."""
    return _import_blocks(block, [ filter.filepath ])

def _import_blocks(block: Block, filepaths: list[str]):
    new_blocks = [ block ]
    for rule in block.get_rules(_NAME):
        filter = _load_filter(rule, filepaths)
        for block in filter.blocks:
            new_blocks += _import_blocks(block, filepaths + [ filter.filepath ])
    return new_blocks

def _load_filter(rule: Rule, filepaths: list[str]):
    filter_filepath = util.parse_rule_filepath(filepaths[-1], rule.description)
    
    if not os.path.exists(filter_filepath):
        util.raise_rule_error(util.DOES_NOT_EXIST_ERROR, rule, filepaths[-1])
    
    if any(os.path.samefile(filepath, filter_filepath) for filepath in filepaths):
        util.raise_rule_error(util.CIRCULAR_REFERENCE_ERROR, rule, filepaths[-1])
    
    return Filter(filter_filepath)