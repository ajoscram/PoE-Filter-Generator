import time, console
from .file_watcher import FileWatcher
from .process_wrapper import ProcessWrapper, ProcessState, Action

_SECONDS_TO_WAIT = 0.1

_RED = "red"
_GREEN = "green"
_YELLOW = "yellow"
_MESSAGE_TEMPLATE = "[{0}]👁\t{1}[/]"
_EXITING_MESSAGE = "Exiting..."
_STARTING_MESSAGE = "Executing..."
_RESTARTING_MESSAGE = "Cancelled execution. Restarting..."
_WAITING_FOR_CHANGES_SUFFIX = " Waiting for changes..."
_FINISHED_SUCESSFULLY_MESSAGE = "Finished successfully!" + _WAITING_FOR_CHANGES_SUFFIX
_FINISHED_UNSUCESSFULLY_MESSAGE = "Finished unsuccessfully." + _WAITING_FOR_CHANGES_SUFFIX

def watch(directory: str, glob: str, action: Action):
    """
    Runs an infinite loop until the user raises a `KeyboardInterrupt`.
    If a file that matches the `path_pattern` within the `directory` is changed,
    the `action` is executed.
    """
    process = ProcessWrapper(action)
    watcher = FileWatcher(directory, glob)
    
    try:
        while True:
            process_state = process.get_state()
            
            if process_state == ProcessState.FINISHED_SUCCESSFULLY:
                _write(_FINISHED_SUCESSFULLY_MESSAGE, _GREEN)
                process.stop()
            
            if process_state == ProcessState.FINISHED_UNSUCCESSFULLY:
                _write(_FINISHED_UNSUCESSFULLY_MESSAGE, _RED)
                process.stop()
            
            if not watcher.notices_change():
                time.sleep(_SECONDS_TO_WAIT)
                continue
                
            if process_state == ProcessState.RUNNING:
                _write(_RESTARTING_MESSAGE)
                process.stop()
            else:
                _write(_STARTING_MESSAGE)

            process.start()

    except KeyboardInterrupt:
        _write(_EXITING_MESSAGE)
        process.stop()

def _write(message: str, color: str = _YELLOW):
    console.write(_MESSAGE_TEMPLATE.format(color, message))