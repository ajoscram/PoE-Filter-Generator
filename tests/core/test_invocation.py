from core.invocation import Invocation

_HANDLER_NAME = "handler"

def test_constructor_given_a_handler_name_should_instantiate_correctly():

    invocation = Invocation(_HANDLER_NAME)

    assert invocation.handler_name == _HANDLER_NAME
    assert invocation.options == []

def test_str_should_return_the_correct_string_representation():
    invocation = Invocation(_HANDLER_NAME)
    invocation.options = [ "option1", "option2" ]

    string = str(invocation)

    assert _HANDLER_NAME in string
    for option in invocation.options:
        assert option in string