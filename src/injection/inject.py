import inspect
import sys
from functools import wraps
from inspect import Signature
from typing import Any, Callable, Coroutine, List, TypeVar, cast

from injection.provide import Provide
from injection.providers import Resource
from injection.providers.base import BaseProvider
from injection.providers.base_factory import BaseFactoryProvider

if sys.version_info < (3, 10):
    from typing_extensions import ParamSpec
else:
    from typing import ParamSpec

P = ParamSpec("P")
T = TypeVar("T")


def get_related_func_scope_resources(
    providers: List[BaseProvider[Any]],
    *,
    match_resource_func: Callable[[Resource[Any]], bool],
) -> List[Resource[Any]]:
    function_scope_resources: List[Resource[Any]] = []

    while providers:
        provider = providers.pop()

        if (
            isinstance(provider, Resource)
            and match_resource_func(provider)
            and provider not in function_scope_resources
        ):
            function_scope_resources.append(provider)

        for related_provider in provider.get_related_providers():
            providers.append(related_provider)

            if isinstance(related_provider, Resource) and match_resource_func(
                related_provider,
            ):
                function_scope_resources.append(related_provider)

    return function_scope_resources


def _get_async_injected(
    f: Callable[P, Coroutine[Any, Any, T]],
    signature: Signature,
) -> Callable[P, Coroutine[Any, Any, T]]:
    @wraps(f)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        providers = []

        for i, (param_name, param) in enumerate(signature.parameters.items()):
            if i < len(args):
                continue

            provide = kwargs.get(param_name, param.default)

            if not isinstance(provide, Provide):
                continue

            provider = provide.provider
            providers.append(provider)

            if isinstance(provider, BaseFactoryProvider):
                if provider.async_mode:
                    resolved_provide = await provider.async_resolve()
                else:
                    resolved_provide = provider()
            else:
                resolved_provide = provider()

            kwargs[param_name] = resolved_provide

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


def _get_sync_injected(
    f: Callable[P, T],
    signature: Signature,
) -> Callable[P, T]:
    @wraps(f)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        providers = []

        for i, (param_name, param) in enumerate(signature.parameters.items()):
            if i < len(args):
                continue

            value_or_provide = kwargs.get(param_name, param.default)

            if not isinstance(value_or_provide, Provide):
                continue

            provider = value_or_provide.provider
            providers.append(provider)
            kwargs[param_name] = provider()

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


def inject(f: Callable[P, T]) -> Callable[P, T]:
    """Decorate callable with injecting decorator"""
    signature = inspect.signature(f)

    if inspect.iscoroutinefunction(f):
        func_with_injected_params = _get_async_injected(f, signature)
        return cast(Callable[P, T], func_with_injected_params)

    return _get_sync_injected(f, signature)
