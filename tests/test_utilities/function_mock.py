import inspect, pathlib, importlib, builtins, os, sys, random, traceback, subprocess, shutil, time, glob, multiprocessing
from types import ModuleType
from typing import Callable
from pytest import MonkeyPatch
from .callable_mock import CallableMock

_PATH_FUNCTION_PREFIX = "_path_"
_KNOWN_MODULES = {
    "_io": builtins,
    "io": builtins,
    "builtins": builtins,
    "ntpath": os.path,
    "genericpath": os.path,
    "os": os,
    "nt": os,
    "sys": sys,
    "random": random,
    "traceback": traceback,
    "subprocess": subprocess,
    "shutil": shutil,
    "time": time,
    "glob": glob,
    "multiprocessing": multiprocessing
}

class FunctionMock(CallableMock):
    """This class monkeypatches a function and collects information on how it is used."""

    def __init__(self, monkeypatch: MonkeyPatch, function_to_mock: Callable, result = None, target = None):
        """The `target` parameter allows direct setting of the mock target.
        If not provided, the module's package is looked for instead."""
        target = target or _get_target_module(function_to_mock)
        function_name = _get_name_to_mock(function_to_mock, target)
        super().__init__(function_name, result)
        monkeypatch.setattr(target, function_name, self)

def _get_name_to_mock(callable: Callable, target: ModuleType):
    return callable.__name__.removeprefix(_PATH_FUNCTION_PREFIX) \
            if target == os.path else callable.__name__

def _get_target_module(obj):
    if module := _try_get_known_module(obj):
        return module
    try:
        module = inspect.getmodule(obj)
        module_path = inspect.getabsfile(module)
        package_name = pathlib.Path(module_path).parts[-2]
        return importlib.import_module(package_name)
    except (ModuleNotFoundError, TypeError):
        raise ModuleNotFoundError(
            f"Could not import '{module.__name__}'. Add it to _KNOWN_MODULES pointing the correct module.")

def _try_get_known_module(obj):
    if obj.__module__ not in _KNOWN_MODULES:
        return None
    
    module = _KNOWN_MODULES[obj.__module__]
    obj_name: str = obj.__name__
    if module == os and obj_name.startswith(_PATH_FUNCTION_PREFIX):
        return os.path

    return module