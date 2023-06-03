from .generator_error import GeneratorError
from .invocation import Invocation

_HANDLER_TAG = "."
_TOO_LITTLE_ARGUMENTS_ERROR = "Too little arguments were provided."
_HANDLER_NOT_PROVIDED_ERROR = "A filter handler was not provided."

class Arguments:
    """Reporesents the arguments passed in through the command line when the generation starts."""
    def __init__(self, args: list[str]):
        if len(args) < 2:
            raise GeneratorError(_TOO_LITTLE_ARGUMENTS_ERROR)
        if args[1].startswith(_HANDLER_TAG):
            args =  [ args[0] ] + args
        if len(args) == 2 or not args[2].startswith(_HANDLER_TAG):
            raise GeneratorError(_HANDLER_NOT_PROVIDED_ERROR)
        
        self.input_filepath: str = args[0]
        self.output_filepath: str = args[1]
        self.invocations = self._get_invocations(args[2:])   
    
    def _get_invocations(self, args: list[str]):
        invocations: list[Invocation] = []
        for arg in args:
            if arg.startswith(_HANDLER_TAG):
                invocations += [ Invocation(arg.lstrip(_HANDLER_TAG)) ]
            else:
                invocations[-1].options += [ arg ]
        return invocations