# Backlog
* Refactor `.econ` and the `ninja` module, so that it is easier to add sieves to any item type
* Add item level support for Allflames
* Add support for gems and memories in `.econ`
* Update `.econ` documentation

* Change the `.import` rule name to something that doesn't need "_" in the file name. Candidates: include, copy
* Add a way to target the input filter's folder in `.import` (a.k.a. absolute pathing)

* Let the RePoE dev know about the following base types not currently being fetched:
    - All harbinger staff pieces
    - Allflame embers

* Add a new command `:publish` to upload filters to GGG with

# Ideas
* Add Wiki to the repo as a submodule, to avoid having to edit via GitHub's poopy editor
* Add E2E testing that actually goes to the internet and does things.
* Update how `ExpectedError`s work:
    - Provide a possible solution alongside the error if possible (maybe?).
    - Define a color scheme for the text in the program and use those rules across all strings shown to the user.
* Use levenshtein distances to improve `:help`'s searching of the correct page.
    If the user types something slightly different than any existing page, then the closest page within a distance threshold is used instead.
* Add a mechanism to emit warnings and return no block on econ if base_types is empty OR add the `.block` rule to split the commented out block from the previous block.
* Add something to `.format` so that it can delete commented out sections of code.
* Express progress of tasks incrementally in the CLI via a progress bar:
    - https://rich.readthedocs.io/en/stable/reference/progress.html#rich.progress.track
    - https://rich.readthedocs.io/en/stable/_modules/rich/progress.html#track
    - https://rich.readthedocs.io/en/stable/_modules/rich/progress.html#Progress.track
    - https://github.com/Textualize/rich/blob/master/examples/downloader.py
    For downloads in particular, the size of each download can be obtained via:
        file_size = int(response.headers['content-length'])