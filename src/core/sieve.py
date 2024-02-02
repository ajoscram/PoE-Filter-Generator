from . import constants
from .expected_error import ExpectedError
from .line import Line

_INT_VALUE_ERROR = "The operand '{0}' expects exactly one number to be provided as a value. Got '{1}' instead."
_BOOL_VALUE_ERROR = "The operand '{0}' expects either 'True' or 'False' to be provided as a value. Got '{1}' instead."

_STR_OPERATOR_ERROR = "The operator '{0}' cannot be used to compare text."
_INT_OPERATOR_ERROR = "The operator '{0}' cannot be used to compare numbers."
_BOOL_OPERATOR_ERROR = "The operator '{0}' cannot be used to compare boolean values."

class Sieve:
    """A Sieve receives a list of lines and allows checking if patterns are contained within them."""
    
    def __init__(self, lines: list[Line] = []):
        self._lines_by_operand: dict[str, list[Line]] = {}
        for line in lines:
            if line.operand not in self._lines_by_operand:
                self._lines_by_operand[line.operand] = [ line ]
            else:
                self._lines_by_operand[line.operand].append(line)
    
    def __contains__(self, pattern: dict[str, str | bool | int]):
        """Checks if a pattern, represented as a dictionary, is contained within the lines of this sieve."""
        for operand, value in pattern.items():
            if not self._is_value_valid(operand, value):
                return False
        return True

    def _is_value_valid(self, operand: str, value: str | bool | int | None):
        if operand not in self._lines_by_operand:
            return True

        for line in self._lines_by_operand[operand]:
            if value != None and line.values == []:
                continue
            if value == None and line.values != []:
                return False
            if type(value) == bool and not _is_bool_value_valid(value, line):
                return False
            elif type(value) == int and not _is_int_value_valid(value, line):
                return False
            elif type(value) == str and not _is_str_value_valid(value, line):
                return False
        
        return True

def _is_bool_value_valid(value: bool, line: Line):
    if len(line.values) != 1 or (line_value := _try_get_bool(line.values[0])) == None:
        error_message = _BOOL_VALUE_ERROR.format(line.operand, " ".join(line.values))
        raise ExpectedError(error_message, line.number)
    
    match line.operator:
        case constants.EQUALS | constants.CONTAINS | "":
            return value == line_value
        case constants.NOT_CONTAINS | constants.NOT_EQUALS:
           return value != line_value
        case _:
            raise ExpectedError(_BOOL_OPERATOR_ERROR.format(line.operator), line.number)
    
def _try_get_bool(text: str):
    match text.lower():
        case "true":
            return True
        case "false":
            return False
        case _:
            return None

def _is_int_value_valid(value: int, line: Line):
    if len(line.values) != 1 or not line.values[0].isdigit():
        error_message = _INT_VALUE_ERROR.format(line.operand, " ".join(line.values))
        raise ExpectedError(error_message, line.number)
    
    line_value = int(line.values[0])
    match line.operator:
        case constants.GREATER_EQUALS:
            return value >= line_value
        case constants.GREATER:
            return value > line_value
        case constants.LESS_EQUALS:
            return value <= line_value
        case constants.LESS:
            return value < line_value
        case constants.CONTAINS | constants.EQUALS | "":
            return value == line_value
        case constants.NOT_CONTAINS | constants.NOT_EQUALS:
            return value != line_value
        case _:
            raise ExpectedError(_INT_OPERATOR_ERROR.format(line.operator), line.number)

def _is_str_value_valid(value: str, line: Line):
    value = value.lower()
    line_values = [ value.replace('"', "").lower() for value in line.values ]
    match line.operator:
        case constants.EQUALS:
            return value in line_values
        case constants.CONTAINS | "":
            return any(line_value in value for line_value in line_values)
        case constants.NOT_CONTAINS | constants.NOT_EQUALS:
            return value not in line_values
        case _:
            raise ExpectedError(_STR_OPERATOR_ERROR.format(line.operator), line.number)