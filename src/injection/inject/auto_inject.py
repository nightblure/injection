import inspect
import sys
from functools import wraps
from typing import Any, Callable, Coroutine, Dict, Optional, Type, TypeVar, Union, cast

from injection.base_container import DeclarativeContainer
from injection.inject.exceptions import DuplicatedFactoryTypeAutoInjectionError
from injection.inject.inject import _resolve_markers
from injection.provide import Provide

if sys.version_info < (3, 10):
    from typing_extensions import ParamSpec
else:
    from typing import ParamSpec

T = TypeVar("T")
P = ParamSpec("P")
Markers = Dict[str, Provide]
_ContainerType = Union[Type[DeclarativeContainer], DeclarativeContainer]


def _resolve_signature_args_with_types_from_container(
    *,
    signature: inspect.Signature,
    target_container: _ContainerType,
) -> Dict[str, Any]:
    resolved_signature_typed_args = {}

    for param_name, param in signature.parameters.items():
        if not (param.annotation is not param.empty and param.default is param.empty):
            continue

        try:
            resolved = target_container.resolve_by_type(param.annotation)
            resolved_signature_typed_args[param_name] = resolved
        except DuplicatedFactoryTypeAutoInjectionError:
            raise

        # Ignore exceptions for cases for example django rest framework
        # endpoint may have parameter 'request' - we don't know how to handle a variety of parameters.
        # But anyway, after this the runtime will fail with an error if something goes wrong
        except Exception:  # noqa: S112
            continue

    return resolved_signature_typed_args


def _get_sync_injected(
    *,
    f: Callable[P, T],
    markers: Markers,
    signature: inspect.Signature,
    target_container: _ContainerType,
) -> Callable[P, T]:
    @wraps(f)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        resolved_signature_typed_args = (
            _resolve_signature_args_with_types_from_container(
                signature=signature,
                target_container=target_container,
            )
        )

        provide_markers = {
            k: v
            for k, v in kwargs.items()
            if k not in markers and isinstance(v, Provide)
        }
        provide_markers.update(markers)
        resolved_values = _resolve_markers(provide_markers)

        kwargs.update(resolved_values)
        kwargs.update(resolved_signature_typed_args)
        return f(*args, **kwargs)

    return wrapper


def _get_async_injected(
    *,
    f: Callable[P, Coroutine[Any, Any, T]],
    markers: Markers,
    signature: inspect.Signature,
    target_container: _ContainerType,
) -> Callable[P, Coroutine[Any, Any, T]]:
    @wraps(f)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        resolved_signature_typed_args = (
            _resolve_signature_args_with_types_from_container(
                signature=signature,
                target_container=target_container,
            )
        )

        provide_markers = {
            k: v
            for k, v in kwargs.items()
            if k not in markers and isinstance(v, Provide)
        }
        provide_markers.update(markers)
        resolved_values = _resolve_markers(provide_markers)

        kwargs.update(resolved_values)
        kwargs.update(resolved_signature_typed_args)
        return await f(*args, **kwargs)

    return wrapper


def auto_inject(
    f: Callable[P, T],
    target_container: Optional[_ContainerType] = None,
) -> Callable[P, T]:
    """Decorate callable with injecting decorator. Inject objects by types"""

    if target_container is None:
        container_subclasses = DeclarativeContainer.__subclasses__()

        if len(container_subclasses) > 1:
            msg = (
                f"Found {len(container_subclasses)} containers, please specify "
                f"the required container explicitly in the parameter 'target_container'"
            )
            raise Exception(msg)

        target_container = container_subclasses[0]

    signature = inspect.signature(f)
    parameters = signature.parameters

    markers = {
        parameter_name: parameter_value.default
        for parameter_name, parameter_value in parameters.items()
        if isinstance(parameter_value.default, Provide)
    }

    if inspect.iscoroutinefunction(f):
        func_with_injected_params = _get_async_injected(
            f=f,
            markers=markers,
            signature=signature,
            target_container=target_container,
        )
        return cast(Callable[P, T], func_with_injected_params)

    return _get_sync_injected(
        f=f,
        markers=markers,
        signature=signature,
        target_container=target_container,
    )
