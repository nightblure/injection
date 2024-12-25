import asyncio
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


async def close_related_function_scope_resources_async(
    providers: List[BaseProvider[Any]],
) -> None:
    async_resources = set()

    while providers:
        provider = providers.pop()

        if (
            isinstance(provider, Resource)
            and provider.initialized
            and provider.function_scope
        ):
            if provider.async_mode:
                async_resources.add(provider)
            else:
                provider.close()

        for related_provider in provider.get_related_providers():
            providers.append(related_provider)

            if not isinstance(related_provider, Resource):
                continue

            match_conditions = [
                related_provider.initialized,
                related_provider.function_scope,
            ]

            if not all(match_conditions):
                continue

            if related_provider.async_mode:
                async_resources.add(related_provider)
            else:
                related_provider.close()

    if len(async_resources) == 0:
        return None

    await asyncio.gather(
        *[resource.async_close() for resource in async_resources],
    )


def close_related_function_scope_resources_sync(
    providers: List[BaseProvider[Any]],
) -> None:
    while providers:
        provider = providers.pop()

        if (
            isinstance(provider, Resource)
            and provider.initialized
            and provider.function_scope
            and not provider.async_mode
        ):
            provider.close()

        for related_provider in provider.get_related_providers():
            providers.append(related_provider)

            if not isinstance(related_provider, Resource):
                continue

            match_conditions = [
                related_provider.initialized,
                related_provider.function_scope,
                not related_provider.async_mode,
            ]

            if not all(match_conditions):
                continue

            related_provider.close()


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
        await close_related_function_scope_resources_async(providers)
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
        close_related_function_scope_resources_sync(providers)
        return result

    return wrapper


def inject(f: Callable[P, T]) -> Callable[P, T]:
    """Decorate callable with injecting decorator"""
    signature = inspect.signature(f)

    if inspect.iscoroutinefunction(f):
        func_with_injected_params = _get_async_injected(f, signature)
        return cast(Callable[P, T], func_with_injected_params)

    return _get_sync_injected(f, signature)
