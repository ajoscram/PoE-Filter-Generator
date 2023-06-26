# Backlog
* Automate deployment on GitHub.
    https://cli.github.com/manual/gh_release_create
    Run the tests. If the tests fail then abort the deployment.
    Create build artifacts via a python script under build/release
* Create an Updater that downloads the most recent release from GitHub.
* Update the GitHub wiki documentation.
* Find a way in the wiki to change the _FILTER_TO_ID_CLASSES_DICT dictionary values from translate.py into a Wiki API call.
    The `translate.py` file in `utils` was left untested because it could be removed if this works.

# Ideas
* Add a `.mods` handler that looks at the classes in a block and returns all mods for them.
* Add a mechanism to emit warnings and return no block on econ if base_types is empty OR add the `.block` rule to split the commented out block from the previous block.
* Add something to `.format` so that it can delete commented out sections of code.
* Add async or multithreaded http fetching for multiple URLs. This should significantly speed up unique searches.