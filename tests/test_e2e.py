import asyncio
from dataclasses import dataclass
from unittest.mock import Mock

from tests.container_objects import func_with_injections


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
    assert container.num() == 144

    callable_result = container.callable_obj(d="sdf")
    partial_callable_result = container.partial_callable(d="sdf")(d="sdfsfwer2")
    assert (5555, 144) == callable_result == partial_callable_result

    coroutine_result = asyncio.run(container.coroutine_provider())
    assert coroutine_result == (1, 2)


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

    # container.reset_singletons()
    # res = container.callable_test_1(d='sfs')
    with container.override_providers(providers_for_overriding, reset_singletons=True):
        redis_url = func_with_injections(2, ddd="sfs")
        assert mock_url == redis_url

    # container.reset_singletons()
    redis_url = func_with_injections(2, ddd="sfs")
    assert redis_url == "redis://localhost"

    # mock redis
    mock_redis = Mock()
    mock_redis.url = "mock_url_tests"
    mock_redis.get.return_value = None
    providers_for_overriding = {"redis": mock_redis}

    _ = container.redis()
    _ = container.settings()

    with container.override_providers(providers_for_overriding):
        assert mock_redis.url == func_with_injections(2, ddd="sfs")
