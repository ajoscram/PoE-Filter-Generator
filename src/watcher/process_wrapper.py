from enum import Enum
from typing import Callable
from multiprocessing import Process

class ProcessState(Enum):
    """Represents the current state of a process being executed within `ProcessWrapper`."""
    NOT_RUNNING = 0
    RUNNING = 1
    FINISHED_SUCCESSFULLY = 2
    FINISHED_UNSUCCESSFULLY = 3

class ProcessWrapper():
    """Manages a `multiprocessing.Process` instance that executes a `Callable`."""
    
    def __init__(self, callable: Callable):
        self._callable = callable
        self._process: Process = None

    def start(self):
        """Instantiates and starts a new process."""
        self._process = Process(target=self._callable)
        self._process.start()
    
    def stop(self):
        """Stops the current wrapped process being executed."""
        if self._process == None:
            return
        self._process.terminate()
        self._process.close()
        self._process = None
    
    def get_state(self) -> ProcessState:
        """Returns the `ProcessState` of the wrapped process."""
        if self._process == None:
            return ProcessState.NOT_RUNNING

        match self._process.exitcode:
            case None:
                return ProcessState.RUNNING
            case 0:
                return ProcessState.FINISHED_SUCCESSFULLY
            case _:
                return ProcessState.FINISHED_UNSUCCESSFULLY