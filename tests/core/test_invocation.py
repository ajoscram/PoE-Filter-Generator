from core.invocation import Invocation

def test_constructor_given_a_handler_name_should_instantiate_correctly():
    HANDLER_NAME = "handler"

    invocation = Invocation(HANDLER_NAME)

    assert invocation.handler_name == HANDLER_NAME
    assert invocation.options == []