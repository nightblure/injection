from dataclasses import dataclass

import pytest

from injection import providers


@dataclass
class SomeClass:
    field1: str
    field2: int

    @classmethod
    async def create(cls, field1: str = "100", field2: int = 500) -> "SomeClass":
        return cls(field1=field1, field2=field2)


def test_singleton_resolving() -> None:
    provider = providers.Singleton(SomeClass, field1="value", field2=1)

    assert provider() is provider()


async def test_singleton_async_resolving() -> None:
    provider = providers.Singleton(SomeClass.create)

    instance_1 = await provider.async_resolve()
    instance_2 = await provider.async_resolve()
    assert instance_1 is instance_2


async def test_singleton_async_resolving_with_params_overriding() -> None:
    provider = providers.Singleton(SomeClass.create)

    value = await provider.async_resolve("test", field2=1000)
    assert isinstance(value, SomeClass)
    assert value.field1 == "test"
    assert value.field2 == 1000


def test_singleton_override_args() -> None:
    singleton_provider = providers.Singleton(SomeClass, field1="value", field2=1)

    resolved = singleton_provider(field1="new_value", field2=100)
    assert resolved.field1 == "new_value"
    assert resolved.field2 == 100

    singleton_provider.reset()
    resolved = singleton_provider()
    assert resolved.field1 == "value"
    assert resolved.field2 == 1


def test_singleton_resolving_with_override_params_not_works_without_reset_cache() -> (
    None
):
    singleton_provider = providers.Singleton(SomeClass, field1="value", field2=1)

    resolved = singleton_provider(field1="new_value", field2=100)
    assert resolved.field1 == "new_value"
    assert resolved.field2 == 100

    resolved = singleton_provider(field1="override_value", field2=239)

    with pytest.raises(AssertionError):
        assert resolved.field1 == "override_value"

    with pytest.raises(AssertionError):
        assert resolved.field2 == 239


def test_singleton_reset_smoke() -> None:
    provider = providers.Singleton(SomeClass, field1="...", field2=-9000)
    obj = provider()
    obj2 = provider()

    assert obj is obj2
    provider.reset()

    obj3 = provider()
    assert obj is not obj3
    assert obj2 is not obj3
