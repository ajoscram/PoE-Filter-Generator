from classes.generator_error import GeneratorError

class Arguments:
    """The arguments class includes all the information passed in through the command line when the generation starts."""

    HANDLER_TAG = "."
    TOO_LITTLE_ARGUMENTS_ERROR = "Too little arguments were provided"
    HANDLER_NOT_FOUND_ERROR = "A filter handler was not provided"

    def __init__(self, args: list[str]):
        if len(args) < 2:
            raise GeneratorError(Arguments.TOO_LITTLE_ARGUMENTS_ERROR)
        self.input_filepath: str = args[0]
        self.output_filepath: str = self.__get_output_file__(args[1])
        self.handler: str = self.__get_handler__(args[1:])
        self.options: list[str] = self.__get_options__(args[1:])

    def __get_output_file__(self, arg: str):
        if not arg.startswith(Arguments.HANDLER_TAG):
            return arg
        else:
            return self.input_filepath

    def __get_handler__(self, args: list[str]):
        if args[0].startswith(Arguments.HANDLER_TAG):
            return args[0].lstrip(Arguments.HANDLER_TAG)
        elif len(args) > 1 and args[1].startswith(Arguments.HANDLER_TAG):
            return args[1].lstrip(Arguments.HANDLER_TAG)
        else:
            raise GeneratorError(Arguments.HANDLER_NOT_FOUND_ERROR)        

    def __get_options__(self, args: list[str]):
        # options always come right after the handler
        if args[0].startswith(Arguments.HANDLER_TAG):
            return args[1:]
        elif len(args) > 1:
            return args[2:]
        else:
            return []