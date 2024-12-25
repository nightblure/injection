import asyncio
import inspect
from collections import defaultdict
from contextlib import contextmanager
from typing import Any, Callable, Dict, Iterator, List, Optional, Type, TypeVar, cast

from injection.exceptions import (
    DuplicatedFactoryTypeAutoInjectionError,
    UnknownProviderTypeAutoInjectionError,
)
from injection.providers import Resource, Singleton
from injection.providers.base import BaseProvider
from injection.providers.base_factory import BaseFactoryProvider

F = TypeVar("F", bound=Callable[..., Any])


class DeclarativeContainer:
    __instance: Optional["DeclarativeContainer"] = None
    __providers: Optional[Dict[str, BaseProvider[Any]]] = None

    @classmethod
    def instance(cls) -> "DeclarativeContainer":
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    @classmethod
    def _get_providers(cls) -> Dict[str, BaseProvider[Any]]:
        if cls.__providers is None:
            cls.__providers = {
                member_name: member
                for member_name, member in inspect.getmembers(cls)
                if isinstance(member, BaseProvider)
            }
        return cls.__providers

    @classmethod
    def get_providers(cls) -> List[BaseProvider[Any]]:
        return list(cls._get_providers().values())

    @classmethod
    def get_resource_providers(cls) -> List[Resource[Any]]:
        return [
            provider
            for provider in cls.get_providers()
            if isinstance(provider, Resource)
        ]

    @classmethod
    @contextmanager
    def override_providers_kwargs(
        cls,
        *,
        reset_singletons: bool = False,
        **providers_for_overriding: Any,
    ) -> Iterator[None]:
        with cls.override_providers(
            providers_for_overriding,
            reset_singletons=reset_singletons,
        ):
            yield

    @classmethod
    @contextmanager
    def override_providers(
        cls,
        providers_for_overriding: Dict[str, Any],
        *,
        reset_singletons: bool = False,
    ) -> Iterator[None]:
        current_providers = cls._get_providers()
        current_provider_names = set(current_providers.keys())
        given_provider_names = set(providers_for_overriding.keys())

        for given_name in given_provider_names:
            if given_name not in current_provider_names:
                msg = f"Provider with name {given_name!r} not found"
                raise RuntimeError(msg)

        # Reset singletons that which were resolved BEFORE the current context
        if reset_singletons:
            cls.reset_singletons()

        for provider_name, mock in providers_for_overriding.items():
            provider = current_providers[provider_name]
            provider.override(mock)

        yield

        for provider_name in providers_for_overriding:
            provider = current_providers[provider_name]
            provider.reset_override()

        # Reset singletons that which were resolved INSIDE the current context
        if reset_singletons:
            cls.reset_singletons()

    @classmethod
    def reset_singletons(cls) -> None:
        providers_gen = cls.get_providers()

        for provider in providers_gen:
            if isinstance(provider, Singleton):
                provider.reset()

    @classmethod
    def reset_override(cls) -> None:
        for provider in cls.get_providers():
            provider.reset_override()

    @classmethod
    def get_provider_by_type(cls, type_: Type[Any]) -> BaseProvider[Any]:
        provider_factory_to_providers = defaultdict(list)

        for provider in cls.get_providers():
            if not issubclass(type(provider), BaseFactoryProvider):
                continue

            provider_factory_to_providers[provider.factory].append(provider)  # type: ignore

            if len(provider_factory_to_providers[provider.factory]) > 1:  # type: ignore
                raise DuplicatedFactoryTypeAutoInjectionError(str(type_))

        for providers in provider_factory_to_providers.values():
            provider = providers[0]
            provider = cast(BaseFactoryProvider[Any], provider)

            if type_ is provider.factory:
                return provider

        raise UnknownProviderTypeAutoInjectionError(str(type_))

    @classmethod
    def resolve_by_type(cls, type_: Type[Any]) -> Any:
        provider = cls.get_provider_by_type(type_)
        return provider()

    @classmethod
    def init_resources(cls) -> None:
        for provider in cls.get_resource_providers():
            if not provider.async_mode:
                provider()

    @classmethod
    async def init_resources_async(cls) -> None:
        await asyncio.gather(
            *[
                provider.async_resolve()
                for provider in cls.get_resource_providers()
                if provider.async_mode
            ],
        )

    @classmethod
    async def init_all_resources(cls) -> None:
        resource_providers = cls.get_resource_providers()

        await asyncio.gather(
            *[
                provider.async_resolve()
                for provider in resource_providers
                if provider.async_mode
            ],
        )

        for provider in resource_providers:
            if not provider.async_mode:
                provider()

    @classmethod
    def close_resources(cls) -> None:
        for provider in cls.get_resource_providers():
            if provider.initialized and not provider.async_mode:
                provider.close()

    @classmethod
    async def close_async_resources(cls) -> None:
        await asyncio.gather(
            *[
                provider.async_close()
                for provider in cls.get_resource_providers()
                if provider.initialized and provider.async_mode
            ],
        )

    @classmethod
    async def close_all_resources(cls) -> None:
        await cls.close_async_resources()
        cls.close_resources()
