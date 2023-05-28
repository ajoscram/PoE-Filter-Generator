# Backlog
* Create unit tests for the entire codebase.
    Create unit tests for handlers
    Create unit tests for ggg, ninja
    Create unit tests for wiki

* Automate deployment on GitHub.
    https://cli.github.com/manual/gh_release_create
    Run the tests. If the tests fail then abort the deployment.
    Create build artifacts via a python script under build/release
    
* Document the Wiki classes.
* Create an Updater that downloads the most recent release from GitHub.

# Ideas
* Add a way to perform custom hide / show blocks.
    Idea: a new rule called "over" (short for overwrite) or "replace" that receives a path to a filter with named blocks that finds and replaces all lines with for lines with the same operators in the input filter's blocks. The blocks selected can be discriminated via a pattern in a rule.

    Idea: introduce a way for some hidden blocks to continue, so that style on hidden blocks can be dealt with later on
    #.if Hide Continue

* Find a way in the wiki to change the _FILTER_TO_ID_CLASSES_DICT dictionary values from translate.py into a Wiki API call.
* Add a mechanism to emit warnings and return no block on econ if base_types is empty OR add the `.block` rule to split the commented out block from the previous block.
* Sometimes just having numbers thrown around can be a little messy (strictness for instance). Perhaps it's a good idea to add some sort of ".var" rule handler.
* Add async or multithreaded http fetching for multiple URLs. This should significantly speed up unique searches.