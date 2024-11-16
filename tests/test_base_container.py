from typing import Generator
from unittest import mock
from unittest.mock import Mock

import pytest

from injection.inject.exceptions import DuplicatedFactoryTypeAutoInjectionError
from injection.providers.base import BaseProvider
from injection.providers.singleton import Singleton
from tests.container_objects import Redis


def test_get_providers(container):
    providers = container.get_providers()

    assert len(providers) > 0

    for provider in providers:
        assert isinstance(provider, BaseProvider)


def test_override_providers_fail_with_unknown_provider(container):
    unknown_provider = "not_exists_provider"
    match = f"Provider with name {unknown_provider!r} not found"
    override_objects = {"not_exists_provider": None}

    with pytest.raises(Exception, match=match):
        with container.override_providers(override_objects):
            ...


def test_override_providers_success(container):
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
            assert container.redis().get() == -999

        override_redis = container.redis()
        assert isinstance(override_redis, Mock)
        assert override_redis.get() == 111
        assert container.num() == 999

    assert not isinstance(container.redis(), Mock)
    assert container.num() == 144


def test_container_instance_is_singleton(container):
    instances = [container.instance() for _ in range(10)]
    instance_ids = {id(instance) for instance in instances}
    assert len(instance_ids) == 1


def test_container_providers_generator(container):
    providers = container._get_providers_generator()
    assert isinstance(providers, Generator)

    for provider in providers:
        assert isinstance(provider, BaseProvider)


def test_reset_singletons(container):
    providers = container._get_providers_generator()

    for provider in providers:
        if isinstance(provider, Singleton):
            provider()
            assert provider._instance is not None

    container.reset_singletons()

    providers = container._get_providers_generator()

    for provider in providers:
        if isinstance(provider, Singleton):
            assert provider._instance is None


def test_reset_override(container):
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


def test_resolve_by_type_expect_error_on_duplicated_provider_types(container):
    # Simulate a duplicate 'redis' provider
    _mock_providers = [container.__dict__["redis"]]
    _mock_providers.extend(
        list(container._get_providers_generator()),
    )

    with mock.patch.object(
        container,
        "_get_providers_generator",
        return_value=_mock_providers,
    ):
        with pytest.raises(DuplicatedFactoryTypeAutoInjectionError):
            container.resolve_by_type(Redis)
