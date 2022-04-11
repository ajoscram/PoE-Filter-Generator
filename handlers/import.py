import os.path

from classes.filter import Filter
from classes.rule import Rule
from classes.section import Section
from common import util

_NAME = "import"

def handle(filter: Filter, section: Section, _):
    """Handles imports of other filter files' sections. Options are ignored."""
    return _import_sections(section, [ filter.filepath ])

def _import_sections(section: Section, filepaths: list[str]):
    new_sections = [ section ]
    for rule in section.get_rules(_NAME):
        filter = _load_filter(rule, filepaths)
        for section in filter.sections:
            new_sections += _import_sections(section, filepaths + [ filter.filepath ])
    return new_sections

def _load_filter(rule: Rule, filepaths: list[str]):
    filter_filepath = util.parse_rule_filepath(filepaths[-1], rule.description)
    
    if not os.path.exists(filter_filepath):
        util.raise_rule_error(util.DOES_NOT_EXIST_ERROR, rule, filepaths[-1])
    
    if any(os.path.samefile(filepath, filter_filepath) for filepath in filepaths):
        util.raise_rule_error(util.CIRCULAR_REFERENCE_ERROR, rule, filepaths[-1])
    
    return Filter(filter_filepath)