import inspect
import sys
from functools import wraps
from inspect import Signature
from typing import Any, Callable, Coroutine, Dict, TypeVar, cast

from injection.provide import Provide

if sys.version_info < (3, 10):
    from typing_extensions import ParamSpec
else:
    from typing import ParamSpec


T = TypeVar("T")
P = ParamSpec("P")
Markers = Dict[str, Provide]


def _resolve_markers(markers: Markers) -> Dict[str, Any]:
    return {param: provide.provider() for param, provide in markers.items()}


def _get_async_injected(
    f: Callable[P, Coroutine[Any, Any, T]],
    signature: Signature,
) -> Callable[P, Coroutine[Any, Any, T]]:
    @wraps(f)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        markers_to_resolve = {}

        for i, (param, value) in enumerate(signature.parameters.items()):
            if i < len(args) or param in kwargs:
                continue

            if not isinstance(value.default, Provide):
                continue

            markers_to_resolve[param] = value.default

        resolved_markers = _resolve_markers(markers_to_resolve)

        for field_name, field_value in kwargs.items():
            if isinstance(field_value, Provide):
                kwargs[field_name] = field_value.provider()

        return await f(*args, **resolved_markers, **kwargs)

    return wrapper


def _get_sync_injected(
    f: Callable[P, T],
    signature: Signature,
) -> Callable[P, T]:
    @wraps(f)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        markers_to_resolve = {}

        for i, (param, value) in enumerate(signature.parameters.items()):
            if i < len(args) or param in kwargs:
                continue

            if not isinstance(value.default, Provide):
                continue

            markers_to_resolve[param] = value.default

        resolved_markers = _resolve_markers(markers_to_resolve)

        for field_name, field_value in kwargs.items():
            if isinstance(field_value, Provide):
                kwargs[field_name] = field_value.provider()

        return f(*args, **resolved_markers, **kwargs)

    return wrapper


def inject(f: Callable[P, T]) -> Callable[P, T]:
    """Decorate callable with injecting decorator"""
    signature = inspect.signature(f)

    if inspect.iscoroutinefunction(f):
        func_with_injected_params = _get_async_injected(f, signature)
        return cast(Callable[P, T], func_with_injected_params)

    return _get_sync_injected(f, signature)
