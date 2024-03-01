from enum import Enum
from abc import ABC, abstractmethod
from multiprocessing import Process

class Action(ABC):
    """Abstract class that represents an action that can be carried out by the watcher.
    Children must implement the `__call__` method."""
    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass

class ProcessState(Enum):
    """Represents the current state of a process being executed within `ProcessWrapper`."""
    NOT_RUNNING = 0
    RUNNING = 1
    FINISHED_SUCCESSFULLY = 2
    FINISHED_UNSUCCESSFULLY = 3

class ProcessWrapper():
    """Manages a `multiprocessing.Process` instance that executes an `Action`."""
    
    def __init__(self, action: Action):
        self.action = action
        self.process: Process = None

    def start(self):
        """Instantiates and starts a new process."""
        self.process = Process(target=self.action)
        self.process.start()
    
    def stop(self):
        """Stops the current wrapped process being executed."""
        if self.process == None:
            return
        self.process.terminate()
        self.process.close()
        self.process = None
    
    def get_state(self) -> ProcessState:
        """Returns the `ProcessState` of the wrapped process."""
        if self.process == None:
            return ProcessState.NOT_RUNNING

        match self.process.exitcode:
            case None:
                return ProcessState.RUNNING
            case 0:
                return ProcessState.FINISHED_SUCCESSFULLY
            case _:
                return ProcessState.FINISHED_UNSUCCESSFULLY