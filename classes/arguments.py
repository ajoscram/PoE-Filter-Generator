from classes.generator_error import GeneratorError

_HANDLER_TAG = "."
_TOO_LITTLE_ARGUMENTS_ERROR = "Too little arguments were provided"
_HANDLER_NOT_FOUND_ERROR = "A filter handler was not provided"

class Arguments:
    """The arguments class includes all the information passed in through the command line when the generation starts."""
    def __init__(self, args: list[str]):
        if len(args) < 2:
            raise GeneratorError(_TOO_LITTLE_ARGUMENTS_ERROR)
        self.input_filepath: str = args[0]
        self.output_filepath: str = self._get_output_file(args[1])
        self.handler: str = self._get_handler(args[1:])
        self.options: list[str] = self._get_options(args[1:])

    def _get_output_file(self, arg: str):
        if not arg.startswith(_HANDLER_TAG):
            return arg
        else:
            return self.input_filepath

    def _get_handler(self, args: list[str]):
        if args[0].startswith(_HANDLER_TAG):
            return args[0].lstrip(_HANDLER_TAG)
        elif len(args) > 1 and args[1].startswith(_HANDLER_TAG):
            return args[1].lstrip(_HANDLER_TAG)
        else:
            raise GeneratorError(_HANDLER_NOT_FOUND_ERROR)        

    def _get_options(self, args: list[str]):
        # options always come right after the handler
        if args[0].startswith(_HANDLER_TAG):
            return args[1:]
        elif len(args) > 1:
            return args[2:]
        else:
            return []