from core import Block, SHOW, HIDE, CLASS, RULE_START, RULE_SEPARATOR, COMMENT_START, EQUALS, BASE_TYPE, GREATER_EQUALS

_LINE_NUMBER = 1
_DEFAULT_BLOCK_LINES = [ SHOW, f"{CLASS} {EQUALS} \"Currency\"", f"{BASE_TYPE} {EQUALS} \"Jeweller's Orb\"" ]

def test_constructor_given_a_line_number_should_instantiate_correctly():
    block = Block(_LINE_NUMBER)

    assert block.line_number == _LINE_NUMBER
    assert block.lines == []

def test_extract_given_no_lines_are_passed_should_return_no_blocks():
    LINES = []

    blocks = Block.extract(LINES)

    assert len(blocks) == 0

def test_extract_given_lines_that_represent_two_blocks_and_a_line_number_should_return_two_blocks():
    ANOTHER_BLOCK = [ HIDE, f"{CLASS} {EQUALS} \"Currency\"" ]

    blocks = Block.extract(_DEFAULT_BLOCK_LINES + ANOTHER_BLOCK)

    assert len(blocks) == 2
    assert len(blocks[0].lines) == len(_DEFAULT_BLOCK_LINES)
    assert len(blocks[1].lines) == len(ANOTHER_BLOCK)

def test_comment_out_should_comment_out_lines_in_the_block():
    block = _create_block(*_DEFAULT_BLOCK_LINES)

    block.comment_out()

    for uncommented_text_line, commented_out_line in zip(_DEFAULT_BLOCK_LINES, block.lines):
        assert uncommented_text_line in commented_out_line.comment

def test_hide_should_set_show_to_hide():
    block = _create_block(SHOW)

    block.hide()

    assert block.lines[0].operand == HIDE

def test_show_should_set_hide_to_show():
    block = _create_block(HIDE)

    block.show()

    assert block.lines[0].operand == SHOW

def test_upsert_given_existing_operand_should_override_values():
    OPERAND = "operand"
    NEW_VALUES = [ "new_value", "another_new_value" ]
    block = _create_block(f'{OPERAND} {EQUALS} old_value')

    block.upsert(OPERAND, NEW_VALUES)

    assert len(block.lines[0].values) == 2
    assert block.lines[0].values == NEW_VALUES

def test_upsert_given_new_operand_should_append_new_line():
    OPERAND = "operand"
    VALUES = [ "first_value", "second_value" ]
    block = _create_block(*_DEFAULT_BLOCK_LINES)

    block.upsert(OPERAND, VALUES, GREATER_EQUALS)

    assert len(block.lines) == len(_DEFAULT_BLOCK_LINES) + 1
    assert block.lines[-1].operand == OPERAND
    assert block.lines[-1].operator == GREATER_EQUALS
    assert block.lines[-1].values == VALUES

def test_get_rules_given_a_line_with_rules_should_return_rules_with_that_name():
    RULE_NAME = "rule"
    block = _create_block(f"{RULE_START}{RULE_NAME} {RULE_SEPARATOR}{RULE_NAME} {RULE_SEPARATOR}another_rule")

    rules = block.get_rules(RULE_NAME)

    assert len(rules) == 2

def test_get_raw_lines_should_return_equivalent_raw_lines():
    block = _create_block(*_DEFAULT_BLOCK_LINES)

    raw_lines = block.get_raw_lines()

    for raw_line in _DEFAULT_BLOCK_LINES:
        assert raw_line in raw_lines

def test_get_sieve_should_return_a_sieve_that_validates_the_lines_in_the_block():
    block = _create_block(*_DEFAULT_BLOCK_LINES, f"{COMMENT_START} a line without an operand")

    sieve = block.get_sieve()

    assert { SHOW: None } in sieve
    assert { CLASS: "Currency" } in sieve
    assert { CLASS: "Something else" } not in sieve

def test_str_overload_should_contain_the_raw_lines():
    block = _create_block(*_DEFAULT_BLOCK_LINES)

    block_str = str(block)

    for raw_line in _DEFAULT_BLOCK_LINES:
        assert raw_line in block_str

def _create_block(*lines: str):
    return Block.extract(lines, _LINE_NUMBER)[0]