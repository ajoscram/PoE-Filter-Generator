from core.constants import SHOW, HIDE, CLASS, RULE_START, RULE_SEPARATOR
from core import Block

_LINE_NUMBER = 1
_DEFAULT_BLOCK_LINES = [ SHOW, f"Class == \"Currency\"", "BaseType == \"Jeweller's Orb\"" ]

def test_constructor_given_a_line_number_should_instantiate_correctly():
    block = Block(_LINE_NUMBER)

    assert block.line_number == _LINE_NUMBER
    assert block.lines == []

def test_extract_given_no_lines_are_passed_should_return_no_blocks():
    LINES = []

    blocks = Block.extract(LINES)

    assert len(blocks) == 0

def test_extract_given_lines_that_represent_two_blocks_and_a_line_number_should_return_two_blocks():
    ANOTHER_BLOCK = [ HIDE, "Class == \"Currency\"" ]

    blocks = Block.extract(_DEFAULT_BLOCK_LINES + ANOTHER_BLOCK)

    assert len(blocks) == 2
    assert len(blocks[0].lines) == len(_DEFAULT_BLOCK_LINES)
    assert len(blocks[1].lines) == len(ANOTHER_BLOCK)

def test_comment_out_should_comment_out_lines_in_the_block():
    block = _create_block(_DEFAULT_BLOCK_LINES)

    block.comment_out()

    for uncommented_text_line, commented_out_line in zip(_DEFAULT_BLOCK_LINES, block.lines):
        assert uncommented_text_line in commented_out_line.comment

def test_hide_should_set_show_to_hide():
    block = _create_block([ SHOW ])

    block.hide()

    assert block.lines[0].operand == HIDE

def test_show_should_set_hide_to_show():
    block = _create_block([ HIDE ])

    block.show()

    assert block.lines[0].operand == SHOW

def test_find_given_an_operand_should_return_lines_with_that_operand():
    OPERAND = "operand"
    LINES = [ f"{OPERAND} == values", "another_operand >= other_values" ]
    block = _create_block(LINES)

    lines_found = block.find(operand=OPERAND)

    assert len(lines_found) == 1

def test_find_given_an_operator_should_return_lines_with_that_operator():
    OPERATOR = "=="
    LINES = [ f"operand {OPERATOR} values", "another_operand >= other_values" ]
    block = _create_block(LINES)

    lines_found = block.find(operator=OPERATOR)

    assert len(lines_found) == 1

def test_get_rules_given_a_line_with_rules_should_return_rules_with_that_name():
    RULE_NAME = "rule"
    LINES = [ f"{RULE_START}{RULE_NAME} {RULE_SEPARATOR}{RULE_NAME} {RULE_SEPARATOR}another_rule" ]
    block = _create_block(LINES)

    rules = block.get_rules(RULE_NAME)

    assert len(rules) == 2

def test_get_classes_given_lines_with_class_operand():
    CLASS_1 = "class1"
    CLASS_2 = "class2"
    LINES = [ f'{CLASS} == "{CLASS_1}" "{CLASS_2}"' ]
    block = _create_block(LINES)

    classes = block.get_classes()

    assert CLASS_1 in classes
    assert CLASS_2 in classes

def test_get_raw_lines_should_return_equivalent_raw_lines():
    block = _create_block(_DEFAULT_BLOCK_LINES)

    raw_lines = block.get_raw_lines()

    for raw_line in _DEFAULT_BLOCK_LINES:
        assert raw_line in raw_lines

def test_str_overload_should_contain_the_raw_lines():
    block = _create_block(_DEFAULT_BLOCK_LINES)

    block_str = str(block)

    for raw_line in _DEFAULT_BLOCK_LINES:
        assert raw_line in block_str

def _create_block(lines: list[str]):
    return Block.extract(lines, _LINE_NUMBER)[0]