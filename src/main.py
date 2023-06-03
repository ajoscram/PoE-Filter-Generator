"""
PoE Filter Generator Main Script

For more information run "python main.py -h".
"""

import sys, traceback
from core import GeneratorError, Arguments, Filter, Generator
from handlers import HANDLERS

HELP_ARG = "-help"
HELP_ARG_SHORT = "-h"
HELP_WARNING = f"Use {HELP_ARG} or {HELP_ARG_SHORT} for more information."
HELP = """
Usage:

    python main.py input.filter [output.filter] .handler [option1 option2 optionN] [.handler2 .handlerN]

If you're using the .exe distribution:

    pfg input.filter [output.filter] .handler [option1 option2 optionN] [.handler2 .handlerN]

Where:
    input.filter:
        The filter file used as an input.
        If the file is in a different directory you must provide the entire path to the file.
    output.filter:
        The name of the file to output the results to.
        You can provide a path to another directory here as well if you like.
        If ommited then the results are output to the input.filter file.
    .handler:
        The name of the handler used to modify the filter.
        For more information on handlers visit the project's wiki at https://github.com/ajoscram/PoE-Filter-Generator/wiki/Handlers.
        Handlers may receive options, which can be provided after the handler's name.
        You may provide multiple handlers to perform in a single invocation of this program."""
UNKNOWN_ERROR_WARNING = """
If your're reading this then an unforseen error has ocurred. Notify me immediately so I can fix it!
Please provide either the following text from the error or a screenshot via an issue on GitHub:

https://github.com/ajoscram/PoE-Filter-Generator/issues/new

Thanks!"""

try:
    raw_args = sys.argv[1:]
    if HELP_ARG in raw_args or HELP_ARG_SHORT in raw_args:
        print(HELP)
        sys.exit()
    args = Arguments(raw_args)

    print(f"\nReading filter file from '{args.input_filepath}'...\n")
    filter = Filter.load(args.input_filepath)

    generator = Generator(HANDLERS)
    for invocation in args.invocations:
        print(f"Applying .{' '.join([invocation.handler_name] + invocation.options)}...")
        filter = generator.generate(filter, args.output_filepath, invocation.handler_name, invocation.options)
    
    print(f"\nSaving filter file to '{args.output_filepath}'...")
    filter.save()

    print("Done!")

except GeneratorError as error:
    print(f"\nERROR: {error}\n\n{HELP_WARNING}")
except Exception as e:
    print(f"\nUNKNOWN ERROR: Oopsie, my bad\n\n{UNKNOWN_ERROR_WARNING}\n")
    traceback.print_tb(e.__traceback__)
    print("\n" + type(e).__name__ + ": " + str(e))