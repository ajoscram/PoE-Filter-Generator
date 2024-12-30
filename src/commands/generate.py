import console
from core import Delimiter, ExpectedError, Filter, Block
from handlers import HANDLERS

NAME = "generate"

_APPLYING_HANDLER_MESSAGE = "Applying {0}..."
_SAVING_FILTER_MESSAGE = "Saving filter..."
_READING_FILTER_MESSAGE = "Reading filter file from '{0}'..."
_FILTER_SAVED_MESSAGE = "Filter saved to '{0}'."

_HANDLER_NOT_FOUND_ERROR = "Handler '{0}' was not found."
_HANDLER_NOT_PROVIDED_ERROR = "No handlers were provided. You must provide at least one handler to modify your filter file."
_TOO_LITTLE_ARGUMENTS_ERROR = "Too little arguments were provided. At least a path to a filter file and a handler to use are expected."

class _HandlerInvocation:
    def __init__(self, handler_name: str):
        self.handler_name = handler_name
        self.options: list[str] = []
    
    def __str__(self):
        return Delimiter.HANDLER_START + ' '.join([self.handler_name] + self.options)

class _Params:
    def __init__(self, input_filepath: str, output_filepath: str, invocations: list[_HandlerInvocation]):
        self.input_filepath = input_filepath
        self.output_filepath = output_filepath
        self.invocations = invocations

def execute(args: list[str]):
    """Applies handlers to `.filter` files and writes the output to a new file.
    Arguments, listed in the order expected:
    - the path to the `.filter` file expected as input.
    - the path where the output should be placed. If none, then the input filepath is used instead.
    - a list of handlers with their respective options (i.e. `.handler1 option1 option2 .handler2 option3 ...`).
        These handlers will be applied to the input filter in regular reading order.
    """
    params = _create_params(args)
    
    console.write(_READING_FILTER_MESSAGE.format(params.input_filepath))
    filter = Filter.load(params.input_filepath)

    for invocation in params.invocations:
        console.write(_APPLYING_HANDLER_MESSAGE.format(invocation))
        filter = _generate_filter(filter, invocation.handler_name, invocation.options)
    
    console.write(_SAVING_FILTER_MESSAGE)
    filter.save(params.output_filepath)

    console.write(_FILTER_SAVED_MESSAGE.format(params.output_filepath), done=True)

def _create_params(args: list[str]):
    if len(args) < 2:
        raise ExpectedError(_TOO_LITTLE_ARGUMENTS_ERROR)
    input_filepath = args[0]

    if args[1].startswith(Delimiter.HANDLER_START):
        args =  [ args[0] ] + args
    output_filepath = args[1]
    
    if len(args) == 2 or not args[2].startswith(Delimiter.HANDLER_START):
        raise ExpectedError(_HANDLER_NOT_PROVIDED_ERROR)
    invocations = _create_invocations(args[2:])
    
    return _Params(input_filepath, output_filepath, invocations)

def _create_invocations(raw_args: list[str]):
    invocations: list[_HandlerInvocation] = []
    for arg in raw_args:
        if arg.startswith(Delimiter.HANDLER_START):
            invocations += [ _HandlerInvocation(arg.lstrip(Delimiter.HANDLER_START)) ]
        else:
            invocations[-1].options += [ arg ]
    return invocations

def _generate_filter(filter: Filter, handler_name: str, options: list[str]):
    if handler_name not in HANDLERS:
        raise ExpectedError(_HANDLER_NOT_FOUND_ERROR.format(handler_name))

    handler = HANDLERS[handler_name]
    generated_raw_lines = [ line
        for block in filter.blocks
        for line in handler(filter, block, options) ]
    return Filter(filter.filepath, Block.extract(generated_raw_lines))