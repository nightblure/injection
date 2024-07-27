import inspect
import sys
from functools import wraps
from typing import Any, Callable, Dict, TypeVar, Union

from injection.provide import Provide
from injection.providers.base import BaseProvider

if sys.version_info >= (3, 9):
    from typing import Annotated, get_args, get_origin
else:
    from typing_extensions import Annotated, get_args, get_origin

F = TypeVar("F", bound=Callable[..., Any])
Markers = Dict[str, Provide]


def _is_fastapi_depends(param: Any) -> bool:
    try:
        import fastapi
    except ImportError:
        fastapi = None
    return fastapi is not None and isinstance(param, fastapi.params.Depends)


def _extract_marker(parameter: inspect.Parameter) -> Union[Any, Provide]:
    marker = parameter.default

    parameter_origin = get_origin(parameter.annotation)
    is_annotated = parameter_origin is Annotated

    if is_annotated:
        marker = get_args(parameter.annotation)[1]

    is_fastapi_depends = _is_fastapi_depends(marker)

    if is_fastapi_depends:
        marker = marker.dependency

    return marker


def _get_markers_from_function(f: F) -> Markers:
    injections = {}
    signature = inspect.signature(f)
    parameters = signature.parameters

    for parameter_name, parameter_value in parameters.items():
        marker = _extract_marker(parameter_value)

        if not isinstance(marker, Provide):
            continue

        injections[parameter_name] = marker

    return injections


def _resolve_provide_marker(marker: Provide) -> BaseProvider:
    if not isinstance(marker, Provide):
        msg = f"Incorrect marker type: {type(marker)!r}. Marker must be either Provide."
        raise TypeError(msg)

    marker_provider = marker.provider

    if not isinstance(marker_provider, BaseProvider):
        msg = f"Incorrect marker type: {type(marker_provider)!r}. Marker parameter must be either BaseProvider."
        raise TypeError(msg)

    return marker_provider


def _extract_provider_values_from_markers(markers: Markers) -> Dict[str, Any]:
    providers = {}

    for param, marker_or_str in markers.items():
        provider = _resolve_provide_marker(marker_or_str)
        provider_value = provider()
        providers[param] = provider_value

    return providers


def _get_async_injected(f: F, markers: Markers) -> F:
    @wraps(f)
    async def wrapper(*args, **kwargs):
        providers = _extract_provider_values_from_markers(markers)
        kwargs.update(providers)
        return await f(*args, **kwargs)

    return wrapper


def _get_sync_injected(f: F, markers: Markers) -> F:
    @wraps(f)
    def wrapper(*args, **kwargs):
        providers = _extract_provider_values_from_markers(markers)
        kwargs.update(providers)
        return f(*args, **kwargs)

    return wrapper


def inject(f: F) -> F:
    """Decorate callable with injecting decorator"""
    markers = _get_markers_from_function(f)

    if inspect.iscoroutinefunction(f):
        func_with_injected_params = _get_async_injected(f, markers)
    else:
        func_with_injected_params = _get_sync_injected(f, markers)

    return func_with_injected_params
