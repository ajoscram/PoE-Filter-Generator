# Backlog

# Ideas
* Find a way in the wiki to change the `_FILTER_TO_ID_CLASSES_DICT` dictionary values from `translate.py` into a Wiki API call.
    The `translate.py` file in `utils` was left untested because it could be removed if this works.
* Add a `.mods` handler that looks at the info in a block and returns all mods available.
https://www.poewiki.net/wiki/Special:CargoTables/mods
https://www.poewiki.net/wiki/Special:CargoTables/mod_spawn_weights
https://www.poewiki.net/wiki/Special:CargoTables/items
Example: https://www.poewiki.net/wiki/Modifier:DamageChilledEnemiesInfluence1

    Account for: item level, class, basetype
    - Get the item tags
    - Get all mods that have those tags
* Use levenshtein distances to improve `-help`'s searching of the correct page.
    If the user types something slightly different then any existing page, then the closest page within a distance threshold is used instead.
    To get the name of all pages the sidebar Markdown page in the Wiki can be used.
* Implement disk-caching for HTTP requests.
* Add a mechanism to emit warnings and return no block on econ if base_types is empty OR add the `.block` rule to split the commented out block from the previous block.
* Add something to `.format` so that it can delete commented out sections of code.
* Add async or multithreaded http fetching for multiple URLs. This should significantly speed up unique searches.
* Express progress of tasks incrementally in the CLI via a progress bar:
    - https://rich.readthedocs.io/en/stable/reference/progress.html#rich.progress.track
    - https://rich.readthedocs.io/en/stable/_modules/rich/progress.html#track
    - https://rich.readthedocs.io/en/stable/_modules/rich/progress.html#Progress.track
    - https://github.com/Textualize/rich/blob/master/examples/downloader.py
    For downloads in particular, the size of each download can be obtained via:
        file_size = int(response.headers['content-length'])