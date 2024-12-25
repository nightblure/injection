from dataclasses import dataclass
from typing import List

import pytest

from injection import DeclarativeContainer, Provide, inject, providers


@dataclass
class SomeClass:
    field1: str
    field2: int

    @classmethod
    async def create(cls, field1: str = "100", field2: int = 500) -> "SomeClass":
        return cls(field1=field1, field2=field2)


@pytest.mark.parametrize(
    "objects_count",
    [2, 3, 5, 10],
)
def test_singleton_resolving(objects_count: int) -> None:
    object_ids: List[int] = []
    provider = providers.Singleton(SomeClass, field1="value", field2=1)

    for _ in range(objects_count):
        resolved = provider()
        object_ids.append(id(resolved))

    assert len(object_ids) == objects_count
    assert len(set(object_ids)) == 1


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


def test_singleton_reset() -> None:
    provider = providers.Singleton(SomeClass, field1="...", field2=-9000)
    obj = provider()
    obj2 = provider()

    assert obj is obj2
    provider.reset()

    obj3 = provider()
    assert obj is not obj3
    assert obj2 is not obj3


def test_singleton_overriding_with_reset_singletons() -> None:
    MOCK_REDIS_URL = "redis://mock"  # noqa: N806
    DEFAULT_REDIS_URL = "redis://default"  # noqa: N806

    @dataclass
    class Settings:
        redis_url: str = DEFAULT_REDIS_URL

    class Redis:
        def __init__(self, url: str):
            self.url = url

    class DIContainer(DeclarativeContainer):
        settings = providers.Singleton(Settings)
        redis = providers.Singleton(Redis, url=settings.provided.redis_url)  # type: ignore[arg-type]

    @inject
    def func(redis: Redis = Provide[DIContainer.redis]) -> str:
        return redis.url

    def test_case_1() -> None:
        DIContainer.settings.override(Settings(redis_url=MOCK_REDIS_URL))

        assert func() == MOCK_REDIS_URL

        DIContainer.settings.reset_override()
        # DIContainer.redis.reset() # FIX OF ASSERTION ERROR

        assert func() == DEFAULT_REDIS_URL  # ASSERTION ERROR

    def test_case_2() -> None:
        assert DIContainer.redis().url == DEFAULT_REDIS_URL

        DIContainer.settings.override(Settings(redis_url=MOCK_REDIS_URL))
        # DIContainer.redis.reset() # FIX OF ASSERTION ERROR

        assert func() == MOCK_REDIS_URL  # ASSERTION ERROR

    def test_case_1_fixed() -> None:
        DIContainer.settings.override(Settings(redis_url=MOCK_REDIS_URL))

        assert func() == MOCK_REDIS_URL

        DIContainer.settings.reset_override()
        DIContainer.redis.reset()  # FIX OF ASSERTION ERROR

        assert func() == DEFAULT_REDIS_URL  # OK

    def test_case_2_fixed() -> None:
        assert DIContainer.redis().url == DEFAULT_REDIS_URL

        with DIContainer.override_providers_kwargs(
            settings=Settings(redis_url=MOCK_REDIS_URL),
            reset_singletons=True,
        ):
            assert func() == MOCK_REDIS_URL  # OK

    with pytest.raises(AssertionError):
        test_case_1()

    with pytest.raises(AssertionError):
        test_case_2()

    test_case_1_fixed()
    test_case_2_fixed()
