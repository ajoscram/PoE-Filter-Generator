# To do
* Refactor the API on lines and blocks. Remove any unsued API.
* Find out why indentation on printed lines works wierdly (especially for rules).
* Document the Wiki classes.
* Add summaries to all public functions and packages across the repo.
* Add a mechanism to emit warnings and return no block on econ if base_types is empty OR add the `.block` rule to split the commented out block from the previous block.
* Find a way in the wiki to change the _FILTER_TO_ID_CLASSES_DICT dictionary values from translate.py into a Wiki API call.
* Create unit tests for the entire codebase.

# Ideas
* Deciding how to hide and show blocks
    When adding duplicate lines to the same block, two things can happen:
    - Conditionals are all accounted for, as if written on the same line
    - Styles are overwritten
    Overall, the whole show / hide mechanic probably needs a separate concept to enforce tailored lines to add in case of a show / hide