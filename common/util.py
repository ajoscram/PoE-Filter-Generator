import os.path, re

from classes.generator_error import GeneratorError
from classes.rule import Rule

DOES_NOT_EXIST_ERROR = "Could not resolve the {0} '{1}' to a filter file on your disk."
CIRCULAR_REFERENCE_ERROR = "The {0} '{1}' creates a circular reference loop."

def parse_rule_filepath(source_filepath: str, rule_filepath: str):
    directory = os.path.dirname(source_filepath)
    directory = re.sub("([\w\.])$", "\\1/", directory)

    rule_filepath = re.sub("\s*>\s*", "/", rule_filepath)
    rule_filepath = re.sub("\s*<\s*", "../", rule_filepath)
    rule_filepath = re.sub("([^\.])\.", "\\1/.", rule_filepath)

    new_filepath = directory + rule_filepath + ".filter"
    new_filepath = re.sub("/[^/]*/\.\.", "", new_filepath)

    return new_filepath

def raise_rule_error(message_template: str, filepath: str, rule: Rule):
    error_message = message_template.format(rule.name, rule.description)
    raise GeneratorError(error_message, rule.line_number, filepath)