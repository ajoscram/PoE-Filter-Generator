import inspect, importlib, pathlib
from typing import Callable
from pytest import MonkeyPatch

class FunctionMock:
    """This class is a reference wrapper to a variable inside it.
    Used to reference variables in closures on tests."""
    def __init__(self, monkeypatch: MonkeyPatch, function_to_mock: Callable, return_value_or_function):
        self._args_received = []
        self._return_value_or_function = return_value_or_function
        self._function_name = function_to_mock.__name__
        module = _find_package_module(function_to_mock)
        monkeypatch.setattr(module, self._function_name, self._mock_function)
    
    def received(self, *args):
        """Returns `True` if all `args` were received during execution.
        If any of them were not, `AssertionError` is raised instead."""
        for arg in args:
            if arg not in self._args_received:
                raise AssertionError(f"'{arg}' was not passed as an argument to '{self._function_name}'.")
        return True
    
    def get_arg(self, type: type):
        """Gets the first argument received during execution that has the `type` passed in."""
        for arg in self._args_received:
            if isinstance(arg, type):
                return arg
        raise AssertionError(f"Could not find argument passed to '{self._function_name}'") 

    def _mock_function(self, *args):
        self._args_received += [ arg for arg in args ]
        if callable(self._return_value_or_function):
            return self._return_value_or_function(*args)
        return self._return_value_or_function

def _find_package_module(function_to_mock: Callable):
    module = inspect.getmodule(function_to_mock)        
    module_path = inspect.getabsfile(module)
    package_name = pathlib.Path(module_path).parts[-2]
    return importlib.import_module(package_name)