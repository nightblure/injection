import inspect
import sys
from functools import wraps
from inspect import Signature
from typing import Any, Callable, Coroutine, List, Type, TypeVar, cast

from injection import DeclarativeContainer
from injection.provide import Provide

if sys.version_info < (3, 10):
    from typing_extensions import ParamSpec
else:
    from typing import ParamSpec


P = ParamSpec("P")
T = TypeVar("T")


def _get_all_di_containers() -> List[Type[DeclarativeContainer]]:
    return DeclarativeContainer.__subclasses__()


def _get_async_injected(
    f: Callable[P, Coroutine[Any, Any, T]],
    signature: Signature,
) -> Callable[P, Coroutine[Any, Any, T]]:
    @wraps(f)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        for i, (param, value) in enumerate(signature.parameters.items()):
            if i < len(args):
                continue

            provide = kwargs.get(param, value.default)

            if not isinstance(provide, Provide):
                continue

            resolved_provide = await provide.provider.async_resolve()
            kwargs[param] = resolved_provide

        result = await f(*args, **kwargs)

        for container in _get_all_di_containers():
            await container.close_all_resources()

        return result

    return wrapper


def _get_sync_injected(
    f: Callable[P, T],
    signature: Signature,
) -> Callable[P, T]:
    @wraps(f)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        for i, (param, value) in enumerate(signature.parameters.items()):
            if i < len(args):
                continue

            value_or_provide = kwargs.get(param, value.default)

            if isinstance(value_or_provide, Provide):
                kwargs[param] = value_or_provide.provider()

        result = f(*args, **kwargs)

        for container in _get_all_di_containers():
            container.close_function_scope_resources()

        return result

    return wrapper


def inject(f: Callable[P, T]) -> Callable[P, T]:
    """Decorate callable with injecting decorator"""
    signature = inspect.signature(f)

    if inspect.iscoroutinefunction(f):
        func_with_injected_params = _get_async_injected(f, signature)
        return cast(Callable[P, T], func_with_injected_params)

    return _get_sync_injected(f, signature)
