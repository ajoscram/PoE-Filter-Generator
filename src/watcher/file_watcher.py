import glob, os

class FileWatcher:
    """Class that can notice changes in files within a directory."""
    def __init__(self, directory: str, globs: list[str]):
        """
        * `directory`: The directory to watch. Subdirectories are watched as well.
        * `globs`: A list of path glob patterns to match.
        """
        self.directory = directory
        self.globs = globs
        self.snapshot: dict[str, float] = None

    def notices_change(self):
        """
        Returns `True` if any of the files monitored has changed.
        `False` otherwise, except the very first invocation which always returns `True`
        because no files had been previously monitored.
        """
        new_snapshot = self._get_snapshot()
        if self.snapshot != new_snapshot:
            self.snapshot = new_snapshot
            return True
        return False

    def _get_snapshot(self):
        filepaths = [ os.path.join(self.directory, filepath)
            for pattern in self.globs
            for filepath in glob.iglob(pattern, root_dir=self.directory, recursive=True, include_hidden=True) ]
        return { filepath: os.stat(filepath).st_mtime for filepath in filepaths }