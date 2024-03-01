import glob, os

class FileWatcher:
    """Class that can notice changes in files within a directory."""
    def __init__(self, directory: str, glob: str):
        """
        * `directory`: The directory to watch. Subdirectories are watched as well.
        * `glob`: A path glob pattern to match.
        """
        self.directory = directory
        self.glob = glob
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
        filepaths = glob.glob(self.glob, root_dir=self.directory, recursive=True, include_hidden=True)
        filepaths = [ os.path.join(self.directory, filepath) for filepath in filepaths ]
        return { filepath: os.stat(filepath).st_mtime for filepath in filepaths }