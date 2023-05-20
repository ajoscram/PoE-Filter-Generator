# Backlog
* Add a way to perform custom hide / show blocks.
    Idea: a new rule called "over" (short for overwrite) or "replace" that receives a path to a filter with named blocks that finds and replaces all lines with for lines with the same operators in the input filter's blocks. The blocks selected can be discriminated via a pattern in a rule.

* Find a way in the wiki to change the _FILTER_TO_ID_CLASSES_DICT dictionary values from translate.py into a Wiki API call.
* Document the Wiki classes.
* Create unit tests for the entire codebase.

# Ideas
* Add async or multithreaded http fetching for multiple URLs. This should significantly speed up unique searches.
* Add a mechanism to emit warnings and return no block on econ if base_types is empty OR add the `.block` rule to split the commented out block from the previous block.