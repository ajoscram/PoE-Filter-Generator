import sys, traceback, commands
from core import ExpectedError
from commands import COMMAND_NAME_PREFIX, DEFAULT_COMMAND_NAME, help

_NO_ARGS_ERROR = "No arguments were provided to PFG."
_COMMAND_NOT_FOUND_ERROR = "Command '{0}' was not found."
_EXPECTED_ERROR_TEMPLATE = "ERROR: {0}"
_EXCEPTION_TEMPLATE = "\n{0}: {1}"
_UNKNOWN_ERROR_MESSAGE = """UNKNOWN ERROR: Oopsie, my bad

If your're reading this then an unforseen error has ocurred. Notify me immediately so I can fix it!
Please provide either the following text from the error or a screenshot via an issue on GitHub:

https://github.com/ajoscram/PoE-Filter-Generator/issues/new

Thanks!"""

def main():
    try:
        print() # print a newline for aesthetics
        
        args = sys.argv[1:]
        if len(args) == 0:
            raise ExpectedError(_NO_ARGS_ERROR)

        if not args[0].startswith(COMMAND_NAME_PREFIX):
            args = [ COMMAND_NAME_PREFIX + DEFAULT_COMMAND_NAME ] + args
        
        command_name = args[0].lstrip(COMMAND_NAME_PREFIX)
        if not command_name in commands.COMMANDS:
            raise ExpectedError(_COMMAND_NOT_FOUND_ERROR.format(args[0]))
        
        command_to_execute = commands.COMMANDS[command_name]
        command_to_execute(args[1:])

    except ExpectedError as error:
        print(_EXPECTED_ERROR_TEMPLATE.format(error), '\n')
        help.execute(None)
    except Exception as e:
        print(_UNKNOWN_ERROR_MESSAGE)
        traceback.print_tb(e.__traceback__)
        print(_EXCEPTION_TEMPLATE.format(type(e).__name__, e))

if __name__ == "__main__":
    main()