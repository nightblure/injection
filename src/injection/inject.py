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


# def _is_fastapi_depends(param: Any) -> bool:
#     try:
#         import fastapi
#     except ImportError:
#         fastapi = None  # type: ignore
#     return fastapi is not None and isinstance(param, fastapi.params.Depends)


# def _extract_marker(parameter: inspect.Parameter) -> Union[Any, Provide]:
#     marker = parameter.default
#
#     parameter_origin = get_origin(parameter.annotation)
#     is_annotated = parameter_origin is Annotated
#
#     if is_annotated:
#         marker = get_args(parameter.annotation)[1]
#
#     is_fastapi_depends = _is_fastapi_depends(marker)
#
#     if is_fastapi_depends:
#         marker = marker.dependency
#
#     return marker


def _get_markers_from_function(f: Callable[P, T]) -> Markers:
    injections = {}
    signature = inspect.signature(f)
    parameters = signature.parameters

    for parameter_name, parameter_value in parameters.items():
        if isinstance(parameter_value.default, Provide):
            injections[parameter_name] = parameter_value.default

    return injections


def _resolve_markers(markers: Markers) -> Dict[str, Any]:
    providers = {}

    for param, provide in markers.items():
        provider_value = provide.provider()
        providers[param] = provider_value

    return providers


def _get_async_injected(
    f: Callable[P, Coroutine[Any, Any, T]],
    markers: Markers,
) -> Callable[P, Coroutine[Any, Any, T]]:
    @wraps(f)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        kwargs_for_resolve = {
            k: v
            for k, v in kwargs.items()
            if k not in markers and isinstance(v, Provide)
        }
        markers.update(kwargs_for_resolve)

        kwarg_values = _resolve_markers(markers)
        kwargs.update(kwarg_values)
        return await f(*args, **kwargs)

    return wrapper


def _get_sync_injected(
    f: Callable[P, T],
    markers: Markers,
) -> Callable[P, T]:
    @wraps(f)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        kwargs_for_resolve = {
            k: v
            for k, v in kwargs.items()
            if k not in markers and isinstance(v, Provide)
        }
        markers.update(kwargs_for_resolve)

        kwarg_values = _resolve_markers(markers)
        kwargs.update(kwarg_values)
        return f(*args, **kwargs)

    return wrapper


def inject(f: Callable[P, T]) -> Callable[P, T]:
    """Decorate callable with injecting decorator"""
    markers = _get_markers_from_function(f)

    if inspect.iscoroutinefunction(f):
        func_with_injected_params = _get_async_injected(f, markers)
        return cast(Callable[P, T], func_with_injected_params)

    return _get_sync_injected(f, markers)
