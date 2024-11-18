import inspect
import sys
from functools import wraps
from typing import Any, Callable, Coroutine, Dict, Optional, Type, TypeVar, Union, cast

from injection.base_container import DeclarativeContainer
from injection.provide import Provide

if sys.version_info < (3, 10):
    from typing_extensions import ParamSpec
else:
    from typing import ParamSpec

T = TypeVar("T")
P = ParamSpec("P")
Markers = Dict[str, Provide]
_ContainerType = Union[Type[DeclarativeContainer], DeclarativeContainer]


def _get_sync_injected(
    *,
    f: Callable[P, T],
    signature: inspect.Signature,
    target_container: _ContainerType,
) -> Callable[P, T]:
    @wraps(f)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        resolved_signature_typed_args = {}

        for i, (param_name, param) in enumerate(signature.parameters.items()):
            if i < len(args) or param_name in kwargs:
                continue

            if not (
                param.annotation is not param.empty and param.default is param.empty
            ):
                continue

            resolved = target_container.resolve_by_type(param.annotation)
            resolved_signature_typed_args[param_name] = resolved

        return f(*args, **resolved_signature_typed_args, **kwargs)

    return wrapper


def _get_async_injected(
    *,
    f: Callable[P, Coroutine[Any, Any, T]],
    signature: inspect.Signature,
    target_container: _ContainerType,
) -> Callable[P, Coroutine[Any, Any, T]]:
    @wraps(f)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        resolved_signature_typed_args = {}

        for i, (param_name, param) in enumerate(signature.parameters.items()):
            if i < len(args) or param_name in kwargs:
                continue

            if not (
                param.annotation is not param.empty and param.default is param.empty
            ):
                continue

            resolved = target_container.resolve_by_type(param.annotation)
            resolved_signature_typed_args[param_name] = resolved

        return await f(*args, **resolved_signature_typed_args, **kwargs)

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

    if inspect.iscoroutinefunction(f):
        func_with_injected_params = _get_async_injected(
            f=f,
            signature=signature,
            target_container=target_container,
        )
        return cast(Callable[P, T], func_with_injected_params)

    return _get_sync_injected(
        f=f,
        signature=signature,
        target_container=target_container,
    )
