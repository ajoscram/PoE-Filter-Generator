# Backlog
* The current version of PFG should be functional. Build it and test it against the proper filter. Fix any issues that could arise.
* Add a way to perform custom hide / show blocks.
    Idea: a new rule called over (short for overwrite), that receives a path to a filter with named blocks that find and replace all lines with for lines with the same operators in the input filter's blocks. The blocks selected can be discriminated via a pattern (maybe a rule?). 
* Add summaries to all public functions and packages across the repo.
* Add a mechanism to emit warnings and return no block on econ if base_types is empty OR add the `.block` rule to split the commented out block from the previous block.
* Document the Wiki classes.
* Find a way in the wiki to change the _FILTER_TO_ID_CLASSES_DICT dictionary values from translate.py into a Wiki API call.
* Create unit tests for the entire codebase.

# Ideas
* Deciding how to hide and show blocks
    When adding duplicate lines to the same block, two things can happen:
    - Conditionals are all accounted for, as if written on the same line
    - Styles are overwritten
    Overall, the whole show / hide mechanic probably needs a separate concept to enforce tailored lines to add in case of a show / hide