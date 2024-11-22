import asyncio
from dataclasses import dataclass
from unittest.mock import Mock

from tests.container_objects import (
    Settings,
    func_with_auto_injections,
    func_with_injections,
)


def test_e2e_success(container):
    func_with_injections(2, ddd="sfs")

    some_svc = container.some_service()
    redis = container.redis()
    service = container.service()

    assert isinstance(redis, container.redis.type_cls)
    assert isinstance(some_svc, container.some_service.type_cls)
    assert isinstance(service, container.service.type_cls)

    assert container.some_service() is some_svc
    assert container.redis() is redis
    assert container.service() is not service
    assert container.num() == 1234

    coroutine_result = asyncio.run(container.coroutine_provider())
    assert coroutine_result == (1, 2)


def test_e2e_auto_inject_success(container):
    redis = container.redis()
    assert redis.url == func_with_auto_injections(2, ddd="sfs")

    class MockRedis:
        def __init__(self):
            self.url = "mock_redis_url"

        def get(self, _): ...

    mock_redis = MockRedis()

    with container.override_providers_kwargs(redis=MockRedis()):
        assert mock_redis.url == func_with_auto_injections(224324, ddd="sdfsdfsdf")

    redis = container.redis()
    assert redis.url != mock_redis.url
    assert redis.url == func_with_auto_injections(2, ddd="sfs")


def test_e2e_override(container):
    assert container.redis().url == container.settings().redis_url

    class AnotherSettings:
        some_const = 144

    @dataclass
    class MockSettings:
        redis_url: str
        redis_port: int = 6379
        nested_settings = AnotherSettings()

    mock_url = "redis://test_override_url"
    mock_settings = MockSettings(redis_url=mock_url)
    providers_for_overriding = {"settings": mock_settings}

    with container.override_providers(providers_for_overriding, reset_singletons=True):
        redis_url = func_with_injections(2, ddd="sfs")
        assert mock_url == redis_url

    redis_url = func_with_injections(2, ddd="sfs")
    assert redis_url == "redis://localhost"

    mock_redis = Mock()
    mock_redis.url = "mock_url_tests"
    mock_redis.get.return_value = None
    providers_for_overriding = {"redis": mock_redis}

    _ = container.redis()
    _ = container.settings()

    with container.override_providers(providers_for_overriding, reset_singletons=True):
        assert mock_redis.url == func_with_injections(2, ddd="sfs")

    mock_settings = Settings(redis_url="mock_redis_url_2")

    with container.override_providers_kwargs(
        settings=mock_settings,
        reset_singletons=True,
    ):
        assert container.redis().url == "mock_redis_url_2"
        assert func_with_injections(2, ddd="sfs") == "mock_redis_url_2"
