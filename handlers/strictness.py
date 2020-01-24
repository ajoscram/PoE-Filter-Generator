"""Handles creation of strictness subfilters.
If a single option is passed then a file is created.
If multiple options are passed then a folder is created instead, with one filter for each option.
The higher the tier the better.

Usage:
    python generate.py input.filter [output.filter] .strictness tier1 [tier2 tierN]
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

TAG = "strictness"

def handle(filepath:str, sections: list, options:list = []):
    """Handles creation of strictness recipe subfilters. This function is always called by a Generator object.
    
    Arguments:
        filepath: filepath where the filter should be output to
        sections: list of Section objects which represent the input file
        options: list of numbers where each determines a strictness value (higher is better)
    """
    try:
        #making sure all options passed are numbers
        for tier in options:
            if not tier.isdigit():
                raise HandlerError(None, "Only integer values are accepted as strictness options.")
        #making sure all rule descriptions include only include integers
        for section in sections:
            for rule in section.rules:
                if rule.tag == TAG and not rule.description.isdigit():
                        raise HandlerError(rule.line_number, "Strictness rules must only include a single integer value.")
        #create a folder called the same as the file if it doesn't exist
        if len(options) > 1:
            filepath += " - " + TAG
            if not os.path.isdir(filepath):
                os.mkdir(filepath)
        #generate a different filter for every strictness tier listed as an option
        for tier in options:
            #make a new file to write to
            filter_file = None
            if len(options) > 1:
                filter_file = open(filepath + "/" + tier + ".filter", "w+")
            else:
                filter_file = open(filepath, 'w+')
            for section in sections:
                for rule in section.rules:
                    if rule.tag == TAG:
                        if int(rule.description) >= int(tier):
                            show_section(section)
                        else:
                            hide_section(section)
                #Write every line in the section to the new file
                for line in section.lines:
                    filter_file.write(line + '\n')
            filter_file.close()
    except FileExistsError:
        raise HandlerError(None, "The path '" + filepath + "' corresponds to an already existing file")