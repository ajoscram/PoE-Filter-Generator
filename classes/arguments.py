from classes.generator_error import GeneratorError
from classes.invocation import Invocation

_HANDLER_TAG = "."
_TOO_LITTLE_ARGUMENTS_ERROR = "Too little arguments were provided"
_HANDLER_NOT_FOUND_ERROR = "A filter handler was not provided"

class Arguments:
    """The arguments class includes all the information passed in through the command line when the generation starts."""
    def __init__(self, args: list[str]):
        if len(args) < 2:
            raise GeneratorError(_TOO_LITTLE_ARGUMENTS_ERROR)
        
        self.input_filepath: str = args[0]
        self.output_filepath: str = args[1] if not args[1].startswith(_HANDLER_TAG) else self.input_filepath

        invocations_start_index = 1 if args[1].startswith(_HANDLER_TAG) else 2
        if invocations_start_index == 2 and len(args) < 3:
            raise GeneratorError(_HANDLER_NOT_FOUND_ERROR)

        self.invocations = self._get_invocations(args[invocations_start_index:])   
    
    def _get_invocations(self, args: list[str]):
        invocations: list[Invocation] = []
        for arg in args:
            if arg.startswith(_HANDLER_TAG):
                invocations += [ Invocation(arg.lstrip(_HANDLER_TAG)) ]
            else:
                invocations[-1].options += [ arg ]
        return invocations