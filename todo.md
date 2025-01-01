# Backlog

* The `:help` message for `.import` AND `.if` is incorrect because the python module ends with `_` and the handler does not. Must resolve

* Add non-significant zeroes to `.index` so that it is impossible to mistake an index number by orders of magnitude when doing CTRL+F.

* Clean up formatting from other rules by:
    * Upserting lines into a block should insert before all blank lines at the end of the block
    * Add something to `.format` so that it can delete commented out sections of code.
    * Add a mechanism to emit warnings and return no block on econ if base_types is empty OR add the `.block` rule to split the commented out block from the previous block.

* Release and update `.import` and `.alias` documentation

* Add Cluster Jewels to `.econ`

* Let the RePoE dev know about the following base types not currently being fetched:
    https://github.com/lvlvllvlvllvlvl/RePoE
    - All harbinger staff pieces
    - Allflame embers
    - Transfigured gems

# Ideas
* Make the `FileCache.clear` method smarter by deleting the files listed in entries instead of the whole directory (?)
* Add a new command `:publish` to upload filters to GGG with
* Add Wiki to the repo as a submodule, to avoid having to edit via GitHub's poopy editor
* Move to Python virtual environments
    - VSCode really didn't like this. This should only be re-tried if it becomes a need in the future.
* Add E2E testing that actually goes to the internet and does things.
* Update how `ExpectedError`s work:
    - Provide a possible solution alongside the error if possible (maybe?).
    - Define a color scheme for the text in the program and use those rules across all strings shown to the user.
* Use levenshtein distances to improve `:help`'s searching of the correct page.
    If the user types something slightly different than any existing page, then the closest page within a distance threshold is used instead.
* Express progress of tasks incrementally in the CLI via a progress bar:
    - https://rich.readthedocs.io/en/stable/reference/progress.html#rich.progress.track
    - https://rich.readthedocs.io/en/stable/_modules/rich/progress.html#track
    - https://rich.readthedocs.io/en/stable/_modules/rich/progress.html#Progress.track
    - https://github.com/Textualize/rich/blob/master/examples/downloader.py
    For downloads in particular, the size of each download can be obtained via:
        file_size = int(response.headers['content-length'])