import console
from core import ExpectedError, Filter, Block
from core.constants import RULE_SEPARATOR as _HANDLER_TAG
from handlers import HANDLERS

NAME = "generate"

_DONE_MESSAGE = "Done!"
_APPLYING_HANDLER_MESSAGE = "Applying {0}..."
_SAVING_FILTER_MESSAGE = "Saving filter file to '{0}'..."
_READING_FILTER_MESSAGE = "Reading filter file from '{0}'..."

_HANDLER_NOT_FOUND_ERROR = "Handler '{0}' was not found."
_HANDLER_NOT_PROVIDED_ERROR = "No handlers were provided. You must provide at least one handler to modify your filter file."
_TOO_LITTLE_ARGUMENTS_ERROR = "Too little arguments were provided. At least a path to a filter file and a handler to use are expected."

class _HandlerInvocation:
    def __init__(self, handler_name: str):
        self.handler_name = handler_name
        self.options: list[str] = []
    
    def __str__(self):
        return _HANDLER_TAG + ' '.join([self.handler_name] + self.options)

class _Args:
    def __init__(self, input_filepath: str, output_filepath: str, invocations: list[_HandlerInvocation]):
        self.input_filepath = input_filepath
        self.output_filepath = output_filepath
        self.invocations = invocations

def execute(raw_args: list[str]):
    args = _create_args(raw_args)
    
    console.write(_READING_FILTER_MESSAGE.format(args.input_filepath), '\n')
    filter = Filter.load(args.input_filepath)

    for invocation in args.invocations:
        console.write(_APPLYING_HANDLER_MESSAGE.format(invocation))
        filter = _generate_filter(filter, args.output_filepath, invocation.handler_name, invocation.options)
    
    console.write(f"\n{_SAVING_FILTER_MESSAGE.format(args.output_filepath)}\n")
    filter.save()

    console.write(_DONE_MESSAGE)

def _create_args(raw_args: list[str]):
    if len(raw_args) < 2:
        raise ExpectedError(_TOO_LITTLE_ARGUMENTS_ERROR)
    input_filepath = raw_args[0]

    if raw_args[1].startswith(_HANDLER_TAG):
        raw_args =  [ raw_args[0] ] + raw_args
    output_filepath = raw_args[1]
    
    if len(raw_args) == 2 or not raw_args[2].startswith(_HANDLER_TAG):
        raise ExpectedError(_HANDLER_NOT_PROVIDED_ERROR)
    invocations = _create_invocations(raw_args[2:])
    
    return _Args(input_filepath, output_filepath, invocations)

def _create_invocations(raw_args: list[str]):
    invocations: list[_HandlerInvocation] = []
    for arg in raw_args:
        if arg.startswith(_HANDLER_TAG):
            invocations += [ _HandlerInvocation(arg.lstrip(_HANDLER_TAG)) ]
        else:
            invocations[-1].options += [ arg ]
    return invocations

def _generate_filter(filter: Filter, output_filepath: str, handler_name: str, options: list[str]):
    if handler_name not in HANDLERS:
        raise ExpectedError(_HANDLER_NOT_FOUND_ERROR.format(handler_name))

    handler = HANDLERS[handler_name]
    generated_raw_lines = [ line
        for block in filter.blocks
        for line in handler(filter, block, options) ]
    return Filter(output_filepath, Block.extract(generated_raw_lines))