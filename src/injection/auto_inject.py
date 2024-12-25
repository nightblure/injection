import inspect
import sys
from functools import wraps
from typing import Any, Callable, Coroutine, Dict, Optional, Type, TypeVar, Union, cast

from injection.base_container import DeclarativeContainer
from injection.inject import get_related_func_scope_resources
from injection.provide import Provide
from injection.providers.base import BaseProvider
from injection.providers.base_factory import BaseFactoryProvider

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
        providers = []

        for i, (param_name, param) in enumerate(signature.parameters.items()):
            if i < len(args) or param_name in kwargs:
                continue

            value_or_provide: Union[Provide, Any] = kwargs.get(
                param_name,
                param.default,
            )
            provider: Optional[BaseProvider[Any]] = None

            if isinstance(value_or_provide, Provide):
                provider = value_or_provide.provider

            is_parameter_for_autoinject = (
                param.annotation is not param.empty and param.default is param.empty
            )

            if is_parameter_for_autoinject:
                provider = target_container.get_provider_by_type(param.annotation)
                kwargs[param_name] = provider()
            else:
                if provider is None:
                    continue

                provider = value_or_provide.provider
                kwargs[param_name] = provider()

            if provider is not None:
                providers.append(provider)

        result = f(*args, **kwargs)

        function_scope_resources = get_related_func_scope_resources(
            providers,
            match_resource_func=lambda p: p.initialized
            and not p.async_mode
            and p.function_scope,
        )

        # close function scope resources
        for resource_provider in function_scope_resources:
            if not resource_provider.async_mode:
                resource_provider.close()

        return result

    return wrapper


def _get_async_injected(  # noqa: C901
    *,
    f: Callable[P, Coroutine[Any, Any, T]],
    signature: inspect.Signature,
    target_container: _ContainerType,
) -> Callable[P, Coroutine[Any, Any, T]]:
    @wraps(f)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:  # noqa: PLR0912, C901
        providers = []

        for i, (param_name, param) in enumerate(signature.parameters.items()):
            if i < len(args) or param_name in kwargs:
                continue

            value_or_provide = kwargs.get(param_name, param.default)
            provider: Optional[BaseProvider[Any]] = None

            if isinstance(value_or_provide, Provide):
                provider = value_or_provide.provider

            is_parameter_for_autoinject = (
                param.annotation is not param.empty and param.default is param.empty
            )

            if is_parameter_for_autoinject:
                provider = target_container.get_provider_by_type(param.annotation)
                kwargs[param_name] = provider()
            else:
                if provider is None:
                    continue

                if isinstance(provider, BaseFactoryProvider):
                    if provider.async_mode:
                        resolved_provide = await provider.async_resolve()
                    else:
                        resolved_provide = provider()
                else:
                    resolved_provide = provider()

                kwargs[param_name] = resolved_provide

            if provider is not None:
                providers.append(provider)

        result = await f(*args, **kwargs)

        function_scope_resources = get_related_func_scope_resources(
            providers,
            match_resource_func=lambda p: p.initialized and p.function_scope,
        )

        # close function scope resources
        for resource_provider in function_scope_resources:
            if resource_provider.async_mode:
                await resource_provider.async_close()
            else:
                resource_provider.close()

        return result

    return wrapper


def auto_inject(
    target_container: Optional[_ContainerType] = None,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorate callable with injecting decorator. Inject objects by types"""

    def wrapper(f: Callable[P, T]) -> Callable[P, T]:
        nonlocal target_container

        if target_container is None:
            container_subclasses = DeclarativeContainer.__subclasses__()

            if len(container_subclasses) > 1:
                msg = (
                    f"Found {len(container_subclasses)} containers, please specify "
                    f"the required container explicitly in the parameter 'target_container'"
                )
                raise Exception(msg)

            target_container = container_subclasses[0]  # pragma: no cover

        signature = inspect.signature(f)

        if inspect.iscoroutinefunction(f):
            func_with_injected_params = _get_async_injected(
                f=f,
                signature=signature,
                target_container=target_container,
            )
            return cast(Callable[P, T], func_with_injected_params)
        else:
            return _get_sync_injected(
                f=f,
                signature=signature,
                target_container=target_container,
            )

    return wrapper