import os, sys, console
from core import ExpectedError, COMMAND_START
from commands import DEFAULT_COMMAND_NAME, COMMANDS

_NO_ARGS_ERROR = "No arguments were provided to PFG."
_COMMAND_NOT_FOUND_ERROR = "Command '{0}' was not found."

def main():
    try:
        console.write() # write a newline for aesthetics
        
        curr_dir =  os.path.abspath(os.path.dirname(sys.argv[0]))
        args = sys.argv[1:]
        if len(args) == 0:
            raise ExpectedError(_NO_ARGS_ERROR)

        if not args[0].startswith(COMMAND_START):
            args = [ COMMAND_START + DEFAULT_COMMAND_NAME ] + args
        
        command_name = args[0].lstrip(COMMAND_START)
        if not command_name in COMMANDS:
            raise ExpectedError(_COMMAND_NOT_FOUND_ERROR.format(args[0]))
        
        command_to_execute = COMMANDS[command_name]
        command_to_execute(curr_dir, args[1:])

    except Exception as error:
        console.err(error)

if __name__ == "__main__":
    main()