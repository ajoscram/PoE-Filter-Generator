import inspect
from typing import Type, TypeVar

T = TypeVar('T')

class _Invocation:
    def __init__(self, *args, **kwargs):
        self.args_received = list(args)
        self.kwargs_received = kwargs

class CallableMock:
    """Represents a mock for any Callable."""
    
    def __init__(self, name: str, result = None):
        """The `result` parameter represents the function resolution.
            It behaves differently depending on the type of the value passed:
            * `Exception`s are raised.
            * `Generator`s and `GeneratorFunction`s yield expectedly.
            * `function`s are invoked with the parameters received passed to them when the mock is invoked.
            * Anything else is returned from the function as a value."""
        self.result = result
        self._name = name
        self._invocations: list[_Invocation] = []
    
    def __call__(self, *args, **kwargs):
        self._invocations += [ _Invocation(*args, **kwargs) ]
        
        if inspect.isgeneratorfunction(self.result):
            self.result = self.result(*args, **kwargs)

        result = next(self.result) if inspect.isgenerator(self.result) else self.result
        
        if _is_exception(result):
            raise result
        
        if callable(result):
            return result(*args, **kwargs)
        
        return result

    def received(self, *args, **kwargs):
        """Returns `True` if all `args` and `kwargs` were received during execution.
        If any of them were not, an `AssertionError` is raised instead."""
        return self._check_args_were_received(*args) and self._check_kwargs_were_received(**kwargs)

    def get_invocation_count(self):
        """Returns the number of times the function got invoked."""
        return len(self._invocations)

    def get_arg(self, type: Type[T], n: int = 0):
        """Gets the `n`th argument received during execution that has the `type` passed in.
        Raises a `ValueError` if none are found."""
        args_received = self._get_args_received()
        args_received += [ value for _, value in self._get_kwargs_received() ]
        args_received = [ arg for arg in args_received if isinstance(arg, type) ]

        if len(args_received) > 0 and n < len(args_received):
            return args_received[n]
        
        raise ValueError(
            f"Could not find {n}th argument of type '{type.__name__}' passed to '{self._name}'")
    
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
                    f"Arg '{arg_to_check}' was not received on '{self._name}': {args_received}")

        return True
    
    def _check_kwargs_were_received(self, **kwargs_to_check):
        kwargs_received = self._get_kwargs_received()
        keys_received = [ key for key, _ in kwargs_received ]

        for key_to_check, value_to_check in kwargs_to_check.items():
            if key_to_check not in keys_received:
                raise AssertionError(
                    f"A kwarg named '{key_to_check}' was not received on '{self._name}': {keys_received}")    
            
            values_received = [ value for key, value in kwargs_received if key == key_to_check ]
            if value_to_check not in values_received:
                raise AssertionError(
                    f"Kwarg '{key_to_check}'='{value_to_check}' was not received on '{self._name}': {kwargs_received}")
        
        return True

def _is_exception(value):
    is_subclass = inspect.isclass(value) and issubclass(value, BaseException)
    return is_subclass or isinstance(value, BaseException)