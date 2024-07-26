import inspect
from contextlib import contextmanager
from typing import Any, Callable, Dict, Iterator, List, TypeVar, Union

from injection.providers import Singleton
from injection.providers.base import BaseProvider

F = TypeVar("F", bound=Callable[..., Any])


class DeclarativeContainer:
    __providers: Dict[str, BaseProvider] = None
    __instance: Union["DeclarativeContainer", None] = None

    @classmethod
    def instance(cls) -> "DeclarativeContainer":
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    @classmethod
    def __get_providers(cls) -> Dict[str, BaseProvider]:
        if cls.__providers is None:
            cls.__providers = {
                member_name: member
                for member_name, member in inspect.getmembers(cls)
                if isinstance(member, BaseProvider)
            }
        return cls.__providers

    @classmethod
    def _get_providers_generator(cls) -> Iterator[BaseProvider]:
        for _, member in inspect.getmembers(cls):
            if isinstance(member, BaseProvider):
                yield member

    @classmethod
    def get_providers(cls) -> List[BaseProvider]:
        return list(cls.__get_providers().values())

    @classmethod
    def get_provider_by_attr_name(cls, provider_name: str) -> BaseProvider:
        providers = cls.__get_providers()
        provider = providers.get(provider_name)

        if provider_name not in providers:
            msg = f"Provider {provider_name!r} not found"
            raise Exception(msg)

        return provider

    @classmethod
    @contextmanager
    def override_providers(
        cls,
        providers_for_overriding: Dict[str, Any],
        *,
        reset_singletons: bool = False,
    ) -> Iterator[None]:
        current_providers = cls.__get_providers()
        current_provider_names = set(current_providers.keys())
        given_provider_names = set(providers_for_overriding.keys())

        for given_name in given_provider_names:
            if given_name not in current_provider_names:
                msg = f"Provider with name {given_name!r} not found"
                raise RuntimeError(msg)

        if reset_singletons:
            cls.reset_singletons()

        for provider_name, mock in providers_for_overriding.items():
            provider = current_providers[provider_name]
            provider.override(mock)

        yield

        for provider_name in providers_for_overriding:
            provider = current_providers[provider_name]
            provider.reset_override()

        if reset_singletons:
            cls.reset_singletons()

    @classmethod
    def reset_singletons(cls) -> None:
        providers_gen = cls._get_providers_generator()

        for provider in providers_gen:
            if isinstance(provider, Singleton):
                provider.reset_cache()

    @classmethod
    def reset_override(cls) -> None:
        providers = cls.__get_providers()

        for provider in providers.values():
            provider.reset_override()
