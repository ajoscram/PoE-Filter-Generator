# Backlog
* Automate deployment on GitHub.
    https://cli.github.com/manual/gh_release_create
    - Create a script for publishing a new release on GH. It should invoke the test and build scripts.
    - Create a GH Action for testing the code. This runs on every commit to master.
    - Create a GH Action for publishing. This is ran manually via CLI or Actions on web.

* Create an Updater that downloads the most recent release from GitHub.

* Update the GitHub wiki documentation.

* Find a way in the wiki to change the _FILTER_TO_ID_CLASSES_DICT dictionary values from translate.py into a Wiki API call.
    The `translate.py` file in `utils` was left untested because it could be removed if this works.

# Ideas
* Add a `.mods` handler that looks at the info in a block and returns all mods available.
https://www.poewiki.net/wiki/Special:CargoTables/mods
https://www.poewiki.net/wiki/Special:CargoTables/mod_spawn_weights
https://www.poewiki.net/wiki/Special:CargoTables/items
Example: https://www.poewiki.net/wiki/Modifier:DamageChilledEnemiesInfluence1

    Account for: item level, class, basetype

    - Get the item tags
    - Get all mods that have those tags

* Add a mechanism to emit warnings and return no block on econ if base_types is empty OR add the `.block` rule to split the commented out block from the previous block.
* Add something to `.format` so that it can delete commented out sections of code.
* Add async or multithreaded http fetching for multiple URLs. This should significantly speed up unique searches.