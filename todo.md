# Backlog
* Implement the `web.download` function and swap out the prints on `console` for rich console usage
* Add the following commands:
    - `-update`: to update the tool to the latest version.
    - `-help`: add support for fetching and displaying wiki pages
* Find a way in the wiki to change the `_FILTER_TO_ID_CLASSES_DICT` dictionary values from `translate.py` into a Wiki API call.
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

* Implement disk-caching for HTTP requests.
* Add a mechanism to emit warnings and return no block on econ if base_types is empty OR add the `.block` rule to split the commented out block from the previous block.
* Add something to `.format` so that it can delete commented out sections of code.
* Add async or multithreaded http fetching for multiple URLs. This should significantly speed up unique searches.