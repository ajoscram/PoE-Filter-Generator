import pytest, math
from core import GeneratorError, Block
from core.constants import COMMENT_START, RULE_SEPARATOR, RULE_START, SHOW
from handlers.choose import _MULTIPLE_COMBINE_RULES_IN_THE_SAME_BLOCK_ERROR,_RULE_PARAMETER_COUNT_ERROR, _SET_SIZE_TOO_LARGE_ERROR, _SET_SIZE_TYPE_ERROR, _SUBSET_SIZE_TOO_LARGE_ERROR, _SUBSET_SIZE_TYPE_ERROR, NAME as CHOOSE
from handlers import choose
from tests.test_utilities.functions import create_filter

def test_handle_given_no_choose_rules_should_return_the_lines_as_is():
    FILTER = create_filter(SHOW)

    lines = choose.handle(FILTER, FILTER.blocks[0], None)

    assert lines[0] == SHOW

def test_handle_given_more_than_one_choose_rule_in_block_should_raise():
    RULES = [ f"{RULE_SEPARATOR} {CHOOSE}", f"{RULE_SEPARATOR} {CHOOSE}" ]
    FILTER = create_filter(f"{COMMENT_START}{' '.join(RULES)}")

    with pytest.raises(GeneratorError) as error:
        _ = choose.handle(FILTER, FILTER.blocks[0], None)

    assert error.value.message == _MULTIPLE_COMBINE_RULES_IN_THE_SAME_BLOCK_ERROR.format(len(RULES))
    assert error.value.line_number == FILTER.blocks[0].lines[0].number

def test_handle_given_not_two_params_should_raise():
    PARAMS = [ "1", "2", "3" ]
    FILTER = create_filter(f"{SHOW} {RULE_START}{CHOOSE} {' '.join(PARAMS)}")

    with pytest.raises(GeneratorError) as error:
        _ = choose.handle(FILTER, FILTER.blocks[0], None)

    assert error.value.message == _RULE_PARAMETER_COUNT_ERROR.format(len(PARAMS))
    assert error.value.line_number == FILTER.blocks[0].lines[0].number


@pytest.mark.parametrize("param_1, param_2, error_message", [
    ("non_digit", "1", _SET_SIZE_TYPE_ERROR),
    ("1", "non_digit", _SUBSET_SIZE_TYPE_ERROR)
])
def test_handle_given_params_are_non_digit_(param_1: str, param_2: str, error_message: str):
    FILTER = create_filter(f"{SHOW} {RULE_START}{CHOOSE} {param_1} {param_2}")

    with pytest.raises(GeneratorError) as error:
        _ = choose.handle(FILTER, FILTER.blocks[0], None)

    assert error.value.message == error_message.format(param_1 if param_2.isdigit() else param_2)
    assert error.value.line_number == FILTER.blocks[0].lines[0].number

def test_handle_given_subset_is_larger_than_set_should_raise():
    SET_SIZE = 0
    SUBSET_SIZE = SET_SIZE + 1
    FILTER = create_filter(f"{SHOW} {RULE_START}{CHOOSE} {SET_SIZE} {SUBSET_SIZE}")

    with pytest.raises(GeneratorError) as error:
        _ = choose.handle(FILTER, FILTER.blocks[0], None)

    assert error.value.message == _SUBSET_SIZE_TOO_LARGE_ERROR.format(SUBSET_SIZE, SET_SIZE)
    assert error.value.line_number == FILTER.blocks[0].lines[0].number

def test_handle_given_set_larger_than_number_of_lines_available_should_raise():
    SET_SIZE = 2
    FILTER = create_filter(f"{SHOW} {RULE_START}{CHOOSE} {SET_SIZE} {SET_SIZE - 1}")

    with pytest.raises(GeneratorError) as error:
        _ = choose.handle(FILTER, FILTER.blocks[0], None)
    
    assert error.value.message == _SET_SIZE_TOO_LARGE_ERROR.format(SET_SIZE, 0)
    assert error.value.line_number == FILTER.blocks[0].lines[0].number

def test_handle_given_combinable_lines_should_return_the_combinations():
    SET_SIZE = 3
    SUBSET_SIZE = SET_SIZE - 1
    FIRST_LINE = f"{SHOW} {RULE_START}{CHOOSE} {SET_SIZE} {SUBSET_SIZE}"
    LINES_TO_COMBINE =  [ FIRST_LINE ] + [ f"\t{number}" for number in range(SET_SIZE) ]
    FILTER = create_filter("\n".join(LINES_TO_COMBINE))

    lines = choose.handle(FILTER, FILTER.blocks[0], None)

    assert len(lines) == _get_expected_line_count(SET_SIZE, SUBSET_SIZE, len(LINES_TO_COMBINE))
    assert len(Block.extract(lines)) == _get_expected_block_count(SET_SIZE, SUBSET_SIZE)

def _get_expected_line_count(set_size: int, subset_size: int, total_line_count: int):
    block_count = _get_expected_block_count(set_size, subset_size)
    return (subset_size + total_line_count - set_size) * block_count

def _get_expected_block_count(set_size: int, subset_size: int):
    # this calculates the binomial coefficient formula
    denominator = math.factorial(subset_size) * math.factorial(set_size - subset_size)
    return math.factorial(set_size) / denominator