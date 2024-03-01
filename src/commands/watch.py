import console, os, sys, watcher
from . import generate
from core import ExpectedError, ERROR_EXIT_CODE

NAME = "watch"

_FILTER_GLOB = "**/*.filter"
_WATCHING_FILES_MESSAGE = "Watching filter files on '{0}'. Press [cyan]CTRL+C[/] to stop."
_INPUT_FILEPATH_ERROR = "The input filter '{0}' does not exist."
_ARGUMENT_COUNT_ERROR = """You must provide at least 3 arguments in the following order:

\t1. The input filter file to read.
\t2. The output filter path to write.
\t3. One or more handlers to execute."""
_OUTPUT_SUBDIRECTORY_OF_INPUT_ERROR = """The output filter's directory is either the same or a subdirectory of the input filter's directory. This would cause an infinite loop.

\tInput filter's directory: [green]{0}[/]
\tOutput filter's directory: [green]{1}[/]"""

class _GenerateAction(watcher.Action):
    def __init__(self, args: list[str]):
        self.args = args
    
    def __call__(self):
        try:
            generate.execute(self.args)
        except Exception as error:
            console.err(error)
            sys.exit(ERROR_EXIT_CODE)

def execute(args: list[str]):
    """Executes the `:generate` command when files within the directory or
    subdirectories of the filter passed are changed."""
    directory = _get_dir_to_watch(args)
    console.write(_WATCHING_FILES_MESSAGE.format(directory))
    watcher.watch(directory, _FILTER_GLOB, _GenerateAction(args))

def _get_dir_to_watch(args: list[str]):
    if len(args) < 3:
        raise ExpectedError(_ARGUMENT_COUNT_ERROR)
    
    if not os.path.isfile(args[0]):
        raise ExpectedError(_INPUT_FILEPATH_ERROR.format(args[0]))
    input_dir = os.path.dirname(os.path.abspath(args[0]))

    output_dir = os.path.dirname(os.path.abspath(args[1]))
    if output_dir.startswith(input_dir):
        raise ExpectedError(_OUTPUT_SUBDIRECTORY_OF_INPUT_ERROR.format(input_dir, output_dir))
    
    return input_dir