import os.path, re

from classes.filter import Filter
from classes.generator_error import GeneratorError
from classes.rule import Rule
from classes.section import Section

NAME = "import"

IMPORT_DOES_NOT_EXIST_ERROR = "Could not resolve the import '{0}' to a filter file on your disk."
CIRCULAR_IMPORT_ERROR = "The import '{0}' creates a circular reference loop."

def handle(filter: Filter, section: Section, _):
    """Handles imports of other filter files. Options are ignored."""
    return __import_sections__(section, [ filter.filepath ])

def __import_sections__(section: Section, filepaths: list[str]):
    new_sections = [ section ]
    for rule in section.get_rules(NAME):
        filter = __load_filter__(rule, filepaths)
        for section in filter.sections:
            new_sections += __import_sections__(section, filepaths + [ filter.filepath ])
    return new_sections

def __load_filter__(rule: Rule, filepaths: list[str]):
    filter_filepath = __get_import_filepath__(filepaths[-1], rule.description)
    
    if not os.path.exists(filter_filepath):
        raise GeneratorError(IMPORT_DOES_NOT_EXIST_ERROR.format(rule.description), rule.line_number, filepaths[-1])
    
    if any(os.path.samefile(filepath, filter_filepath) for filepath in filepaths):
        raise GeneratorError(CIRCULAR_IMPORT_ERROR.format(rule.description), rule.line_number, filepaths[-1])
    
    return Filter(filter_filepath)

def __get_import_filepath__(source_filepath: str, rule_filepath: str):
    directory = os.path.dirname(source_filepath)
    directory = re.sub("([\w\.])$", "\\1/", directory)

    rule_filepath = re.sub("\s*>\s*", "/", rule_filepath)
    rule_filepath = re.sub("\s*<\s*", "../", rule_filepath)
    rule_filepath = re.sub("(.)\.", "\\1/.", rule_filepath)

    import_filepath = directory + rule_filepath + ".filter"
    import_filepath = re.sub("/[^/]*/\.\.", "", import_filepath)

    return import_filepath