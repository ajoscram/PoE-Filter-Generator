# Backlog
* Add documentation for the `.game` handler.
* Replace `.econ` mnemonics for the block's classes using a sieve.
    Update .econ documentation.
* Refactor places where the Sieve class can be used (like UniqueFilter)
* Let the RePoE dev know about the following base types not currently being fetched:
    - All harbinger staff pieces

# Ideas
* Add a new command `:publish` to upload filters to GGG with
* Use levenshtein distances to improve `:help`'s searching of the correct page.
    If the user types something slightly different than any existing page, then the closest page within a distance threshold is used instead.
    The sidebar Markdown page in the Wiki can be used to get the name of all pages.
* Add a mechanism to emit warnings and return no block on econ if base_types is empty OR add the `.block` rule to split the commented out block from the previous block.
* Add something to `.format` so that it can delete commented out sections of code.
* Express progress of tasks incrementally in the CLI via a progress bar:
    - https://rich.readthedocs.io/en/stable/reference/progress.html#rich.progress.track
    - https://rich.readthedocs.io/en/stable/_modules/rich/progress.html#track
    - https://rich.readthedocs.io/en/stable/_modules/rich/progress.html#Progress.track
    - https://github.com/Textualize/rich/blob/master/examples/downloader.py
    For downloads in particular, the size of each download can be obtained via:
        file_size = int(response.headers['content-length'])