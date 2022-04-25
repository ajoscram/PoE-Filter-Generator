"""PoE Filter Generator Main Script

This script is the one called to run the program.
For more information run "python generate.py -h".
"""

import sys, traceback

from classes.arguments import Arguments
from classes.generator import Generator
from classes.filter import Filter
from classes.generator_error import GeneratorError

HELP_ARG = "-help"
HELP_ARG_SHORT = "-h"
HELP_WARNING = f"Use {HELP_ARG} or {HELP_ARG_SHORT} for more information."
HELP = """
Usage:

    python generate.py input.filter [output.filter] .handler [option1 option2 optionN]

If you're using the .exe distribution:

    pfg input.filter [output.filter] .handler [option1 option2 optionN]

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
        Handlers may receive options, which can be provided after the handler's name."""
UNKNOWN_ERROR_WARNING = """If your're reading this then an unforseen error has ocurred. Notify me immediately so I can fix it!
Please provide either the following text from the error or a screenshot via an issue on GitHub:

https://github.com/ajoscram/PoE-Filter-Generator/issues/new

Thanks!"""

try:
    raw_args = sys.argv[1:]
    if HELP_ARG in raw_args or HELP_ARG_SHORT in raw_args:
        print(HELP)
        sys.exit()
    args = Arguments(raw_args)

    print(f"\nReading filter file from '{args.input_filepath}'...")
    filter = Filter(args.input_filepath)

    print(f"Generating filter with .{' '.join([args.handler] + args.options)}...")
    generator = Generator()
    filter = generator.generate(filter, args.handler, args.options)
    
    print(f"Saving filter file to '{args.output_filepath}'...")
    filter.save(args.output_filepath)

    print("\nDone!")

except GeneratorError as error:
    print(f"\nERROR: {error}\n\n{HELP_WARNING}")
except Exception as e:
    print(f"\nUNKNOWN ERROR: Oopsie, my bad\n\n{UNKNOWN_ERROR_WARNING}\n")
    traceback.print_tb(e.__traceback__)
    print("\n" + type(e).__name__ + ": " + str(e))