"""
PoE Filter Generator Main Script

For more information run "python main.py -h".
"""

import sys, traceback
from core import GeneratorError, Filter, Generator, Arguments
from handlers import HANDLERS

_HELP_ARG = "-help"
_HELP_ARG_SHORT = "-h"
_HELP_MESSAGE = "\nVisit https://github.com/ajoscram/PoE-Filter-Generator/wiki#usage for more information about this tool's usage."
_UNKNOWN_ERROR_MESSAGE = """
UNKNOWN ERROR: Oopsie, my bad

If your're reading this then an unforseen error has ocurred. Notify me immediately so I can fix it!
Please provide either the following text from the error or a screenshot via an issue on GitHub:

https://github.com/ajoscram/PoE-Filter-Generator/issues/new

Thanks!"""
_GENERATOR_ERROR_TEMPLATE = "\nERROR: {0}\n{1}"
_EXCEPTION_TEMPLATE = "\n{0}: {1}"

_READING_FILTER_MESSAGE = "\nReading filter file from '{0}'...\n"
_APPLYING_HANDLER_MESSAGE = "Applying .{0}..."
_SAVING_FILTER_MESSAGE = "\nSaving filter file to '{0}'..."
_DONE_MESSAGE = "Done!"

def main():
    try:
        raw_args = sys.argv[1:]
        if _HELP_ARG in raw_args or _HELP_ARG_SHORT in raw_args:
            print(_HELP_MESSAGE)
            sys.exit()
        args = Arguments(raw_args)

        print(_READING_FILTER_MESSAGE.format(args.input_filepath))
        filter = Filter.load(args.input_filepath)

        generator = Generator(HANDLERS)
        for invocation in args.invocations:
            print(_APPLYING_HANDLER_MESSAGE.format(invocation))
            filter = generator.generate(
                filter, args.output_filepath, invocation.handler_name, invocation.options)
        
        print(_SAVING_FILTER_MESSAGE.format(args.output_filepath))
        filter.save()

        print(_DONE_MESSAGE)

    except GeneratorError as error:
        print(_GENERATOR_ERROR_TEMPLATE.format(error, _HELP_MESSAGE))
    except Exception as e:
        print(_UNKNOWN_ERROR_MESSAGE)
        traceback.print_tb(e.__traceback__)
        print(_EXCEPTION_TEMPLATE.format(type(e).__name__, e))

if __name__ == "__main__":
    main()