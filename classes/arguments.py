"""Module that exports the arguments class only."""

from classes.generator_error import GeneratorError

class Arguments:
    """The arguments class includes all the information passed in through the command line when the generation starts."""

    HANDLER_TAG = "."
    TOO_LITTLE_ARGUMENTS_ERROR = "Too little arguments were provided"
    HANDLER_NOT_FOUND_ERROR = "A filter handler was not provided"

    def __init__(self, raw_args: list):
        if len(raw_args) < 2:
            raise GeneratorError(Arguments.TOO_LITTLE_ARGUMENTS_ERROR)
        self.input_filepath: str = raw_args[0]
        self.output_filepath: str = self.__get_output_file__(raw_args[1])
        self.handler: str = self.__get_handler__(raw_args[1], raw_args[2])
        self.options: list[str] = self.__get_options__(raw_args)

    def __get_output_file__(self, arg: str):
        if not arg.startswith(Arguments.HANDLER_TAG):
            return arg
        else:
            return self.input_filepath

    def __get_handler__(self, arg_1: str, arg_2: str):
        if arg_1.startswith(Arguments.HANDLER_TAG):
            return arg_1.lstrip(Arguments.HANDLER_TAG)
        elif arg_2.startswith(Arguments.HANDLER_TAG):
            return arg_2.lstrip(Arguments.HANDLER_TAG)
        else:
            raise GeneratorError(Arguments.HANDLER_NOT_FOUND_ERROR)        

    def __get_options__(self, args: list):
        # options always come right after the handler
        if len(args) > 2 and args[1].startswith(Arguments.HANDLER_TAG):
            return args[2:]
        elif len(args) > 2:
            return args[3:]
        else:
            return []