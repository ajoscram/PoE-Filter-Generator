from dataclasses import dataclass, field
from core import Block, Line, Rule, ExpectedError
from .context import Context

NAME = "multi"
_END_PARAM = "end"
_PREMATURE_END_PARAM_ERROR = "The 'end' parameter can only be used in the last .multi rule of a block."

@dataclass
class _BlockParts:
    prefix: list[Line]
    suffix: list[Line] = field(default_factory=lambda: [])
    multis: list[list[Line]] = field(default_factory=lambda: [])

def handle(block: Block, context: Context):
    """Generates multiple block from a single one."""
    rules = block.get_rules(NAME)
    if len(rules) in [0, 1]:
        return [ str(line) for line in block.lines ]
    
    parts = _get_block_parts(rules, block, context.filter.filepath)
    return [ str(line)
        for multi in parts.multis
        for line in parts.prefix + multi + parts.suffix ]

def _get_block_parts(rules: list[Rule], block: Block, filepath: str):
    multis = _get_multis(rules, block, filepath)
    
    prefix_line_index = rules[0].line_number - block.line_number
    prefix = block.lines[:prefix_line_index]

    suffix_line_index = rules[-1].line_number - block.line_number + 1 \
        if _has_end_param(rules[-1]) else len(block.lines)
    suffix = block.lines[suffix_line_index:]
    
    return _BlockParts(prefix, suffix, multis)

def _has_end_param(rule: Rule):
    return rule.description.lower().strip() == _END_PARAM

def _get_multis(rules: list[Rule], block: Block, filepath: str):
    multis = []
    for rule_index, rule in enumerate(rules):
        line_index = rule.line_number - block.line_number

        if _has_end_param(rule):
            if rule != rules[-1]:
                raise ExpectedError(_PREMATURE_END_PARAM_ERROR, rule.line_number, filepath)
            
            multis[-1] += [block.lines[line_index]]
            break

        end_line_index = rules[rule_index + 1].line_number - block.line_number \
            if rule != rules[-1] else len(block.lines)
        multis += [ block.lines[line_index : end_line_index] ]

    return multis