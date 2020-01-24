"""Handles creation of chaos recipe subfilters.
If a single option is passed then a file is created.
If multiple options are passed then a folder is created instead, with one filter for each option.

Usage:
    python generate.py input.filter [output.filter] .chaos option1 [option2 optionN]
Output (single file):
    - output.filter
Output (multifile):
    output.filter (folder)
    - option1.filter
    - option2.filter
    - optionN.filter
"""
import os

from classes.section import Section
from classes.rule import Rule
from classes.handler_error import HandlerError
from .__functions__ import hide_section
from .__functions__ import show_section

TAG = "chaos"

def handle(filepath:str, sections: list, options:list = []):
    """Handles creation of chaos recipe subfilters. This function is always called by a Generator object.
    
    Arguments:
        filepath: filepath where the filter should be output to
        sections: list of Section objects which represent the input file
        options: list of strings where each shows all .chaos sections that include the option
    """
    try:
        #create a folder called the same as the file if it doesn't exist
        if len(options) > 1:
            filepath += " - " + TAG
            if not os.path.isdir(filepath):
                os.mkdir(filepath)
        #generate a different filter for every base type listed as an option
        for base in options:
            #make a new file to write to
            filter_file = None
            if len(options) > 1:
                filter_file = open(filepath + "/" + base + ".filter", "w+")
            else:
                filter_file = open(filepath, 'w+')
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
        raise HandlerError(None, "The path '" + filepath + "' corresponds to an already existing file")