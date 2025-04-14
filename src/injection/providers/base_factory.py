import inspect
import sys
from typing import (
    Any,
    Awaitable,
    Callable,
    TypeVar,
    Union,
    cast,
)

if sys.version_info < (3, 10):
    from typing_extensions import ParamSpec
else:
    from typing import ParamSpec

from injection.providers.base import BaseProvider
from injection.resolving import resolve_provider_args, resolve_provider_args_async

P = ParamSpec("P")
T = TypeVar("T")


def _is_async_factory(factory: Callable[P, T]) -> bool:
    return any(
        [
            inspect.iscoroutinefunction(factory),
            inspect.isasyncgenfunction(factory),
        ],
    )


class BaseFactoryProvider(BaseProvider[T]):
    def __init__(
        self,
        factory: Union[Callable[P, T], Callable[P, Awaitable[T]]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._factory = factory
        self._is_async_factory = _is_async_factory(factory)

    @property
    def is_async_factory(self) -> bool:
        return self._is_async_factory

    @property
    def factory(self) -> Union[Callable[P, T], Callable[P, Awaitable[T]]]:
        return self._factory  # type: ignore[return-value]

    async def _async_resolve(self, *args: Any, **kwargs: Any) -> T:
        """
        Positional arguments are appended after Factory positional dependencies.
        Keyword arguments have the priority over the Factory keyword dependencies with the same name.
        """
        resolved_args, resolved_kwargs = await resolve_provider_args_async(
            *self._args,
            **self._kwargs,
        )
        resolved_kwargs.update(kwargs)

        if self._is_async_factory:
            instance = await self._factory(*resolved_args, *args, **resolved_kwargs)  # type: ignore[misc]
        else:
            instance = self._factory(*resolved_args, *args, **resolved_kwargs)

        return cast(T, instance)

    def _resolve(self, *args: Any, **kwargs: Any) -> T:
        """
        Positional arguments are appended after Factory positional dependencies.
        Keyword arguments have the priority over the Factory keyword dependencies with the same name.
        """
        resolved_args, resolved_kwargs = resolve_provider_args(
            *self._args,
            **self._kwargs,
        )
        resolved_kwargs.update(kwargs)
        instance = self._factory(*resolved_args, *args, **resolved_kwargs)
        return cast(T, instance)

    def has_async_dependencies(self) -> bool:
        dependencies = self.get_dependencies()

        for provider in dependencies:
            if not isinstance(provider, BaseFactoryProvider):
                continue

            if provider._is_async_factory:
                return True

        return False

    @property
    def should_be_async_resolved(self) -> bool:
        return self._is_async_factory or self.has_async_dependencies()
