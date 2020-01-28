"""PoE Filter Generator Main Script

This script is the one called to run the program.
For more information run "python generate.py -h".
"""

# Standard libs
import sys, traceback, copy
# Local
from classes.generator import Generator, GeneratorError
from classes.section import SectionError
from classes.rule import RuleError
from classes.handler_error import HandlerError

class CommandError(Exception):
    """Class for command line parsing exception handling."""

    #Error message constants
    TOO_LITTLE_ARGUMENTS = "Too little arguments were provided"
    HANDLER_NOT_FOUND = "A filter handler was not provided"

    def __init__(self, message: str):
        """Takes an error message from the caller."""
        self.message = message

HANDLER_TAG = "."
UNKNOWN_ERROR_WARNING = """If your're reading this then an unforseen error has ocurred. Notify me immediately so I can fix it!
Please provide either the following text from the error or a screenshot.
Post an issue on GitHub (preferable): https://github.com/ajoscram/PoE-Filter-Generator/issues/new
Let me know on Twitter: @ajoscram
Thanks!"""
HELP_WARNING = "Use -help or -h for more information."
HELP_ARG_SHORT = "-h"
HELP_ARG = "-help"
HELP = """
Usage:

    python generate.py input.filter [output.filter] .handler [option1 option2 optionN]

If you're using the .exe distribution:

    poe-filter-generator input.filter [output.filter] .handler [option1 option2 optionN]

Note: items inside square brackets are optional.

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
        For more information on handlers visit the project's wiki at https://github.com/ajoscram/PoE-Filter-Generator/wiki/Handlers#what-are-handlers.
        Handlers may receive options, which can be provided after the handler's name."""

try:
    args = sys.argv[1:]
    #look for a help arg, if found only display help and nothing else
    for arg in args:
        if arg == HELP_ARG or arg == HELP_ARG_SHORT:
            print(HELP)
            exit()
    #at least 2 arguments must be provided:
    #   1) the name of the input file, always first
    #   2) the name of the output filepath (optional)
    #   3) a filter handler name (.handler)
    #   4) filter handler options (optional, could be any amount of these) 
    if len(args) < 2:
        raise CommandError(CommandError.TOO_LITTLE_ARGUMENTS)
    
    #the first argument must always be the input filter file
    input_file = args[0]
    
    #the output filename could be skipped, in which case it is the same as the input filename
    output_file = ""
    if args[1].startswith(HANDLER_TAG):
        output_file = input_file
    else:
        output_file = args[1]
    
    #the handler must be either the second or third parameter
    handler = ""
    if args[1].startswith(HANDLER_TAG):
        handler = args[1].lstrip(HANDLER_TAG)
    elif args[2].startswith(HANDLER_TAG):
        handler = args[2].lstrip(HANDLER_TAG)
    else:
        raise CommandError(CommandError.HANDLER_NOT_FOUND)
    
    #the options for the handler are, well, optional and must start at the third or fourth parameter
    options = []
    if len(args) > 2 and args[1].startswith(HANDLER_TAG):
        options = args[2:]
    elif len(args) > 3:
        options = args[3:]

    #run the filter generation
    generator = Generator()
    print("\nExtracting sections from file...")
    sections = generator.sectionize(input_file)
    sections_copy = copy.deepcopy(sections)
    print("Generating filter(s)...")
    generator.generate(output_file, sections, handler, options)
    print("\nDone!")
except CommandError as e:
    print("\nERROR: " + e.message + '\n\n' + HELP_WARNING)
except GeneratorError as e:
    print("\nERROR: " + e.message + "\n\n\tOn file: " + e.filepath + "\n\n" + HELP_WARNING)
except (SectionError, RuleError) as e:
    print("\nERROR: " + e.message + "\n\n\tOn line: " + str(e.line_number) + "\n\n" + HELP_WARNING)
except HandlerError as e:
    #the file must be returned to its original state if its the same
    if input_file == output_file:
        filter_file = open(input_file, 'w+')
        for section in sections_copy:
            for line in section.lines:
                filter_file.write(line + '\n')
    #print the error
    error = ""
    if e.has_line_number():
        error = "\nERROR: " + e.message + "\n\n\tOn line: " + str(e.line_number) + "\n\n" + HELP_WARNING
    else:
        error = print("\nERROR: " + e.message + '\n\n' + HELP_WARNING)
    print(error)
except Exception as e:
    print("\nUNKNOWN ERROR: Oopsie, my bad\n\n" + UNKNOWN_ERROR_WARNING + "\n")
    traceback.print_tb(e.__traceback__)
    print("\n" + type(e).__name__ + ": " + str(e))