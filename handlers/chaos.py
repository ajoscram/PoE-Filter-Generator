import os

from classes.section import Section
from classes.rule import Rule
from classes.handler_error import HandlerError
from .__functions__ import hide_section
from .__functions__ import show_section

TAG = "chaos"

def handle(filepath:str, sections: list, options:list = []):
    try:
        #create a folder called the same as the file if it doesn't exist
        if not os.path.isdir(filepath + " - " + TAG):
            os.mkdir(filepath + " - " + TAG)
        #Sneak in this option to obtain a filter without any chaos recipe bases
        #generate a different filter for every base type listed as an option
        for base in options:
            #make a new file to write to
            filter_file = open(filepath + " - " + TAG + "/" + base + ".filter", "w+")
            for section in sections:
                for rule in section.rules:
                    if rule.tag == TAG:
                        if base in rule.description:
                            show_section(section)
                        elif not base in rule.description:
                            hide_section(section)
                #Write every line in the section to the new file
                for line in section.lines:
                    filter_file.write(line + '\n')
            filter_file.close()
    except FileExistsError:
        raise HandlerError(None, "The path '" + filepath + " - chaos' corresponds to an already existing file")