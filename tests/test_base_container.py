from typing import Type
from unittest import mock
from unittest.mock import Mock

import pytest

from injection.exceptions import DuplicatedFactoryTypeAutoInjectionError
from injection.providers.base import BaseProvider
from injection.providers.singleton import Singleton
from tests.container_objects import Container, Redis


def test_get_providers(container: Type[Container]) -> None:
    providers = container.get_providers()

    assert len(providers) > 0

    for provider in providers:
        assert isinstance(provider, BaseProvider)


def test_override_providers_fail_with_unknown_provider(
    container: Type[Container],
) -> None:
    unknown_provider = "not_exists_provider"
    match = f"Provider with name {unknown_provider!r} not found"
    override_objects = {"not_exists_provider": None}

    with pytest.raises(Exception, match=match):
        with container.override_providers(override_objects):
            ...


def test_override_providers_success(container: Type[Container]) -> None:
    mock_redis = Mock()
    mock_redis.get.return_value = 111
    override_objects = {"redis": mock_redis, "num": 999}
    _ = container.redis()

    with container.override_providers(override_objects):
        mock_redis = Mock()
        mock_redis.get.return_value = -999
        nested_override_objects = {"redis": mock_redis, "num": 92934}

        with container.override_providers(nested_override_objects):
            assert container.num() == 92934
            assert container.redis().get(None) == -999

        override_redis = container.redis()
        assert isinstance(override_redis, Mock)
        assert override_redis.get() == 111
        assert container.num() == 999

    assert not isinstance(container.redis(), Mock)
    assert container.num() == 1234


def test_container_instance_is_singleton(container: Type[Container]) -> None:
    instances = [container.instance() for _ in range(10)]
    instance_ids = {id(instance) for instance in instances}
    assert len(instance_ids) == 1


def test_container_providers(container: Type[Container]) -> None:
    providers = container.get_providers()
    assert isinstance(providers, list)

    for provider in providers:
        assert isinstance(provider, BaseProvider)


def test_reset_singletons(container: Type[Container]) -> None:
    providers = container.get_providers()

    for provider in providers:
        if isinstance(provider, Singleton):
            provider()
            assert provider._instance is not None

    container.reset_singletons()

    providers = container.get_providers()

    for provider in providers:
        if isinstance(provider, Singleton):
            assert provider._instance is None


def test_reset_override(container: Type[Container]) -> None:
    original_num_value = container.num()
    original_num2_value = container.num2()

    container.num.override(2200)
    container.num2.override(99900)

    assert len(container.num._mocks) == 1
    assert len(container.num2._mocks) == 1
    assert container.num() == 2200
    assert container.num2() == 99900

    container.reset_override()

    assert len(container.num._mocks) == 0
    assert len(container.num2._mocks) == 0
    assert container.num() == original_num_value
    assert container.num2() == original_num2_value


def test_resolve_by_type(
    container: Type[Container],
) -> None:
    resolved = container.resolve_by_type(Redis)

    assert isinstance(resolved, Redis)


def test_resolve_by_type_expect_error_on_duplicated_provider_types(
    container: Type[Container],
) -> None:
    # Simulate a duplicate 'redis' provider
    _mock_providers = [container.__dict__["redis"]]
    _mock_providers.extend(
        container.get_providers(),
    )

    with mock.patch.object(
        container,
        "get_providers",
        return_value=_mock_providers,
    ):
        with pytest.raises(DuplicatedFactoryTypeAutoInjectionError):
            container.resolve_by_type(Redis)


def test_sync_resources_lifecycle(container: Type[Container]) -> None:
    container.init_resources()

    assert all(
        provider.initialized
        for provider in container.get_resource_providers()
        if not provider.should_be_async_resolved
    )

    container.close_resources()

    assert all(
        not provider.initialized
        for provider in container.get_resource_providers()
        if not provider.should_be_async_resolved
    )


async def test_async_resources_lifecycle(container: Type[Container]) -> None:
    await container.init_resources_async()

    for provider in container.get_resource_providers():
        if provider.should_be_async_resolved:
            assert provider.initialized

    await container.close_async_resources()

    for provider in container.get_resource_providers():
        if provider.should_be_async_resolved:
            assert not provider.initialized


async def test_init_all_resources(container: Type[Container]) -> None:
    await container.init_all_resources()

    for provider in container.get_resource_providers():
        assert provider.initialized
