import builtins, inspect, importlib, pathlib, os, sys, traceback
from typing import Callable
from pytest import MonkeyPatch

_KNOWN_MODULES = {
    "io": builtins,
    "builtins": builtins,
    "ntpath": os.path,
    "genericpath": os.path,
    "os": os,
    "sys": sys,
    "traceback": traceback
}

class _Invocation:
    def __init__(self, *args, **kwargs):
        self.args_received = list(args)
        self.kwargs_received = kwargs

class FunctionMock:
    """This class monkey patches a function and collects information how it is used."""

    def __init__(self, monkeypatch: MonkeyPatch, function_to_mock: Callable, result = None, target = None):
        """The `result` parameter represents the function resolution.
        It behaves differently depending on the type of the value passed:
        * `Exception`s are raised.
        * `function`s are invoked with the parameters received passed to them when the mock is invoked.
        * Anything else is returned from the function as a value.
        
        The `target` parameter allows direct setting of the mock target.
        If not provided, the module's package module is looked for instead."""
        self.result = result
        self._invocations: list[_Invocation] = []
        self._function_name = function_to_mock.__name__
        target = target or _find_package_module(function_to_mock)
        monkeypatch.setattr(target, self._function_name, self._mock_function)
    
    def received(self, *args, **kwargs):
        """Returns `True` if all `args` and `kwargs` were received during execution.
        If any of them were not, an `AssertionError` is raised instead."""
        return self._check_args_were_received(*args) and self._check_kwargs_were_received(**kwargs)
    
    def get_arg(self, type: type):
        """Gets the first argument received during execution that has the `type` passed in.
        Raises a `ValueError` if none are found."""
        args_received = self._get_args_received()
        args_received += [ value for _, value in self._get_kwargs_received() ]
        args_received = [ arg for arg in args_received if isinstance(arg, type) ]

        if len(args_received) > 0:
            return args_received[0]
        
        raise ValueError(
            f"Could not find argument of type '{type.__name__}' passed to '{self._function_name}'")
    
    def get_invocation_count(self):
        return len(self._invocations)

    def _mock_function(self, *args, **kwargs):
        self._invocations += [ _Invocation(*args, **kwargs) ]
        if _is_exception(self.result):
            raise self.result
        if callable(self.result):
            return self.result(*args, **kwargs)
        return self.result
    
    def _get_args_received(self):
        return [ arg
            for invocation in self._invocations
            for arg in invocation.args_received ]
    
    def _get_kwargs_received(self):
        return [ key_value_pair
            for invocation in self._invocations
            for key_value_pair in invocation.kwargs_received.items() ]

    def _check_args_were_received(self, *args_to_check):
        args_received = self._get_args_received()

        for arg_to_check in args_to_check:
            if arg_to_check not in args_received:
                raise AssertionError(
                    f"Arg '{arg_to_check}' was not received on '{self._function_name}': {args_received}")

        return True

    def _check_kwargs_were_received(self, **kwargs_to_check):
        kwargs_received = self._get_kwargs_received()
        keys_received = [ key for key, _ in kwargs_received ]

        for key_to_check, value_to_check in kwargs_to_check.items():
            if key_to_check not in keys_received:
                raise AssertionError(
                    f"A kwarg named '{key_to_check}' was not received on '{self._function_name}': {keys_received}")    
            
            values_received = [ value for key, value in kwargs_received if key == key_to_check ]
            if value_to_check not in values_received:
                raise AssertionError(
                    f"Kwarg '{key_to_check}'='{value_to_check}' was not received on '{self._function_name}': {kwargs_received}")
        
        return True

def _find_package_module(function_to_mock: Callable):
    if function_to_mock.__module__ in _KNOWN_MODULES:
        return _KNOWN_MODULES[function_to_mock.__module__]    
    try:
        module = inspect.getmodule(function_to_mock)
        module_path = inspect.getabsfile(module)
        package_name = pathlib.Path(module_path).parts[-2]
        return importlib.import_module(package_name)
    except (ModuleNotFoundError, TypeError):
        raise ModuleNotFoundError(
            f"Could not import '{module.__name__}'. Add it to _KNOWN_MODULES pointing the correct module.")

def _is_exception(value):
    is_subclass = inspect.isclass(value) and issubclass(value, Exception)
    return is_subclass or isinstance(value, Exception)