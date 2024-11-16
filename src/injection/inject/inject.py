import inspect
import sys
from functools import wraps
from typing import Any, Callable, Coroutine, Dict, TypeVar, cast

from injection.provide import Provide

if sys.version_info < (3, 10):
    from typing_extensions import ParamSpec
else:
    from typing import ParamSpec


T = TypeVar("T")
P = ParamSpec("P")
Markers = Dict[str, Provide]


def _get_markers_from_function(f: Callable[P, T]) -> Markers:
    signature = inspect.signature(f)
    parameters = signature.parameters

    injections = {
        parameter_name: parameter_value.default
        for parameter_name, parameter_value in parameters.items()
        if isinstance(parameter_value.default, Provide)
    }

    return injections


def _resolve_markers(markers: Markers) -> Dict[str, Any]:
    return {param: provide.provider() for param, provide in markers.items()}


def _get_async_injected(
    f: Callable[P, Coroutine[Any, Any, T]],
    markers: Markers,
) -> Callable[P, Coroutine[Any, Any, T]]:
    @wraps(f)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        provide_markers = {
            k: v
            for k, v in kwargs.items()
            if k not in markers and isinstance(v, Provide)
        }
        provide_markers.update(markers)
        resolved_values = _resolve_markers(provide_markers)

        kwargs.update(resolved_values)
        return await f(*args, **kwargs)

    return wrapper


def _get_sync_injected(
    f: Callable[P, T],
    markers: Markers,
) -> Callable[P, T]:
    @wraps(f)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        provide_markers = {
            k: v
            for k, v in kwargs.items()
            if k not in markers and isinstance(v, Provide)
        }
        provide_markers.update(markers)
        resolved_values = _resolve_markers(provide_markers)

        kwargs.update(resolved_values)
        return f(*args, **kwargs)

    return wrapper


def inject(f: Callable[P, T]) -> Callable[P, T]:
    """Decorate callable with injecting decorator"""
    markers = _get_markers_from_function(f)

    if inspect.iscoroutinefunction(f):
        func_with_injected_params = _get_async_injected(f, markers)
        return cast(Callable[P, T], func_with_injected_params)

    return _get_sync_injected(f, markers)
