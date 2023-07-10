import handlers
from core import GeneratorError, Filter, Block
from core.constants import RULE_SEPARATOR as _HANDLER_TAG

NAME = "g"

_DONE_MESSAGE = "Done!"

_TOO_LITTLE_ARGUMENTS_ERROR = "Too little arguments were provided."
_HANDLER_NOT_PROVIDED_ERROR = "No handlers was not provided."
_READING_FILTER_MESSAGE = "Reading filter file from '{0}'..."
_APPLYING_HANDLER_MESSAGE = "Applying .{0}..."
_SAVING_FILTER_MESSAGE = "Saving filter file to '{0}'..."
_HANDLER_NOT_FOUND_ERROR = "Handler '{0}' was not found."

class _HandlerInvocation:
    def __init__(self, handler_name: str):
        self.handler_name = handler_name
        self.options: list[str] = []
    
    def __str__(self):
        return ' '.join([self.handler_name] + self.options)

class _Args:
    def __init__(self, input_filepath: str, output_filepath: str, invocations: list[_HandlerInvocation]):
        self.input_filepath = input_filepath
        self.output_filepath = output_filepath
        self.invocations = invocations

def execute(raw_args: list[str]):
    args = _create_args(raw_args)
    
    print(_READING_FILTER_MESSAGE.format(args.input_filepath), '\n')
    filter = Filter.load(args.input_filepath)

    for invocation in args.invocations:
        print(_APPLYING_HANDLER_MESSAGE.format(invocation))
        filter = _apply_handler(filter, args.output_filepath, invocation.handler_name, invocation.options)
    
    print(f"\n{_SAVING_FILTER_MESSAGE.format(args.output_filepath)}\n")
    filter.save()

    print(_DONE_MESSAGE)

def _create_args(raw_args: list[str]):
    if len(raw_args) < 2:
        raise GeneratorError(_TOO_LITTLE_ARGUMENTS_ERROR)
    
    if raw_args[1].startswith(_HANDLER_TAG):
        raw_args =  [ raw_args[0] ] + raw_args
    
    if len(raw_args) == 2 or not raw_args[2].startswith(_HANDLER_TAG):
        raise GeneratorError(_HANDLER_NOT_PROVIDED_ERROR)
    
    invocations = _create_invocations(raw_args[2:])
    return _Args(raw_args[0], raw_args[1], invocations)

def _create_invocations(raw_args: list[str]):
    invocations: list[_HandlerInvocation] = []
    for arg in raw_args:
        if arg.startswith(_HANDLER_TAG):
            invocations += [ _HandlerInvocation(arg.lstrip(_HANDLER_TAG)) ]
        else:
            invocations[-1].options += [ arg ]
    return invocations

def _apply_handler(filter: Filter, output_filepath: str, handler_name: str, options: list[str]):
    if handler_name not in handlers.HANDLERS:
        raise GeneratorError(_HANDLER_NOT_FOUND_ERROR.format(handler_name))

    handler = handlers.HANDLERS[handler_name]
    generated_raw_lines = [ line
        for block in filter.blocks
        for line in handler(filter, block, options) ]
    return Filter(output_filepath, Block.extract(generated_raw_lines))