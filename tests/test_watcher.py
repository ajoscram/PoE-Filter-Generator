import pytest, time, watcher, os, glob, console
from watcher.functions import _EXITING_MESSAGE
from test_utilities import FunctionMock
from multiprocessing import Process
from pytest import MonkeyPatch
from enum import Enum

_DIRECTORY = "directory"
_GLOB_PATTERNS = [ "file_pattern.txt" ]

class _StopLoopException(Exception):
    pass

class _LoopEvent(Enum):
    NONE = 0
    CHANGE = 1
    STOP = 2
    INTERRUPT = 3

class _OSStatMock:
    def __init__(self, st_mtime: float):
        self.st_mtime = st_mtime
    
    @classmethod
    def sequence(cls, events: list[_LoopEvent]):
        stat = 0
        for event in events:
            if event == _LoopEvent.STOP:
                raise _StopLoopException()
            if event == _LoopEvent.INTERRUPT:
                raise KeyboardInterrupt()
            stat += event.value
            yield _OSStatMock(stat)

class _ProcessMock:
    def __init__(self, exitcode: int = None):
        self.exitcode = exitcode
        self.times_started = 0
        self.times_terminated = 0
        self.times_closed = 0

    def start(self):
        self.times_started += 1

    def terminate(self):
        self.times_terminated += 1
    
    def close(self):
        self.times_closed += 1

@pytest.fixture(autouse=True)
def stop_mock(monkeypatch: MonkeyPatch):
    return FunctionMock(monkeypatch, time.sleep)

@pytest.fixture(autouse=True)
def glob_mock(monkeypatch: MonkeyPatch):
    return FunctionMock(monkeypatch, glob.iglob, [ "file.txt" ])

@pytest.mark.parametrize("exitcode", [ 0, 1 ])
def test_watch_given_process_finished_should_close_it(monkeypatch: MonkeyPatch, exitcode: int):
    EVENTS = [ _LoopEvent.STOP ]

    process_mock = _execute_watcher_loop(monkeypatch, EVENTS, exitcode)

    assert process_mock.times_started == 1
    assert process_mock.times_closed == 1
    assert process_mock.times_terminated == 1

def test_watch_given_no_changes_should_sleep_and_loop(monkeypatch: MonkeyPatch, stop_mock: FunctionMock):
    EVENTS = [ _LoopEvent.NONE, _LoopEvent.STOP ]

    process_mock = _execute_watcher_loop(monkeypatch, EVENTS)

    assert process_mock.times_started == 1
    assert stop_mock.get_invocation_count() == 1

def test_watch_given_change_and_process_running_should_restart(monkeypatch: MonkeyPatch):
    EVENTS = [ _LoopEvent.CHANGE, _LoopEvent.STOP ]

    process_mock = _execute_watcher_loop(monkeypatch, EVENTS)

    assert process_mock.times_started == 2
    assert process_mock.times_closed == 1
    assert process_mock.times_terminated == 1

@pytest.mark.parametrize("events, times_stopped", [
    ([ _LoopEvent.INTERRUPT ], 0),
    ([ _LoopEvent.CHANGE, _LoopEvent.INTERRUPT ], 1)
])
def test_watch_given_keyboard_interrupt_should_exit(
    monkeypatch: MonkeyPatch, events: list[_LoopEvent], times_stopped: int):
    
    console_write_mock = FunctionMock(monkeypatch, console.write)
    with monkeypatch.context() as context:
        process_mock = _ProcessMock()
        _ = FunctionMock(monkeypatch, Process.__new__, process_mock, Process)
        _ = FunctionMock(context, os.stat, _OSStatMock.sequence(events))

        watcher.watch(_DIRECTORY, _GLOB_PATTERNS, lambda: None)

        message = console_write_mock.get_arg(str, times_stopped)
        assert _EXITING_MESSAGE in message
        assert console_write_mock.get_invocation_count() == times_stopped + 1
        assert process_mock.times_terminated == times_stopped
        assert process_mock.times_closed == times_stopped

def test_watch_should_check_for_changes_in_directory(monkeypatch: MonkeyPatch, glob_mock: FunctionMock):
    EVENTS = [ _LoopEvent.STOP ]

    _execute_watcher_loop(monkeypatch, EVENTS)

    assert glob_mock.get_invocation_count() == 2
    for pattern in _GLOB_PATTERNS:
        assert glob_mock.received(pattern, root_dir=_DIRECTORY, recursive=True)

def _execute_watcher_loop(monkeypatch: MonkeyPatch, events: list[_LoopEvent], exitcode: int = None):
    
    # prepending change here, since a first loop is always needed for these tests to start a process
    events = [ _LoopEvent.CHANGE ] + events
    
    with monkeypatch.context() as context:
        process_mock = _ProcessMock(exitcode)
        _ = FunctionMock(monkeypatch, Process.__new__, process_mock, Process)
        _ = FunctionMock(context, os.stat, _OSStatMock.sequence(events))

        with pytest.raises(_StopLoopException):
            watcher.watch(_DIRECTORY, _GLOB_PATTERNS, lambda: None)

        return process_mock