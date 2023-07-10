from core import ExpectedError

MESSAGE = "message"
LINE_NUMBER = 1
FILEPATH = "filepath"

def test_constructor_should_set_the_values_passed_in():
    error = ExpectedError(MESSAGE, LINE_NUMBER, FILEPATH)

    assert error.message == MESSAGE
    assert error.line_number == LINE_NUMBER
    assert error.filepath == FILEPATH

def test_str_overload_should_contain_all_information_passed():
    error = ExpectedError(MESSAGE, LINE_NUMBER, FILEPATH)

    error_string = str(error)

    assert MESSAGE in error_string
    assert str(LINE_NUMBER) in error_string
    assert FILEPATH in error_string