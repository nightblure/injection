from types import TracebackType
from typing import AsyncContextManager, ContextManager, Optional, Type

import pytest

from injection import Provide, inject
from injection.providers import Resource
from tests.container_objects import Container, Resources


def test_resource_sync_generator() -> None:
    provider = Resource(Resources().sync_generator)

    assert not provider.async_mode
    assert not provider.initialized

    resource_instance = provider()

    assert provider.initialized
    assert isinstance(resource_instance, Resources)
    assert resource_instance.active

    resource_instance.set_value(-1000)
    assert resource_instance._value == -1000

    assert not resource_instance.closed

    provider.close()

    assert not resource_instance.active
    assert resource_instance.closed


async def test_resource_async_generator() -> None:
    provider = Resource(Resources().async_generator)

    assert provider.async_mode
    assert not provider.initialized

    resource_instance = await provider.async_resolve()
    assert provider.initialized
    assert isinstance(resource_instance, Resources)
    assert resource_instance.active

    resource_instance.set_value(-1000)
    assert resource_instance._value == -1000

    assert not resource_instance.closed

    await provider.async_close()

    assert not resource_instance.active
    assert resource_instance.closed


def test_resource_sync_ctx_manager() -> None:
    provider = Resource(Resources().sync_ctx)

    assert not provider.async_mode
    assert not provider.initialized

    resource_instance = provider()

    assert provider.initialized
    assert isinstance(resource_instance, Resources)
    assert resource_instance.active

    resource_instance.set_value(-1000)
    assert resource_instance._value == -1000

    assert not resource_instance.closed

    provider.close()

    assert not resource_instance.active
    assert resource_instance.closed


async def test_resource_async_ctx_manager() -> None:
    provider = Resource(Resources().async_ctx)

    assert provider.async_mode
    assert not provider.initialized

    resource_instance = await provider.async_resolve()

    assert provider.initialized
    assert isinstance(resource_instance, Resources)
    assert resource_instance.active

    resource_instance.set_value(-1000)
    assert resource_instance._value == -1000

    assert not resource_instance.closed

    await provider.async_close()

    assert not resource_instance.active
    assert resource_instance.closed


def test_resource_global_scope(
    container: Type[Container],
) -> None:
    provider = container.sync_resource

    @inject
    def _inner(
        value: Resources = Provide[provider],
    ) -> None:
        assert provider.initialized
        assert provider._context is not None

        assert value.active
        assert not value.closed

    _inner()

    assert provider.initialized
    assert provider._context is not None

    assert provider.instance.active
    assert not provider.instance.closed


def test_resource_function_scope(container: Type[Container]) -> None:
    provider = container.sync_resource_func_scope

    @inject
    def _inner(
        value: Resources = Provide[provider],
    ) -> None:
        assert provider.initialized
        assert provider._context is not None

        assert value.active
        assert not value.closed

    _inner()

    assert not provider.initialized
    assert provider._context is None

    assert not provider.instance.active
    assert provider.instance.closed


async def test_resource_global_scope_async(
    container: Type[Container],
) -> None:
    provider = container.async_resource

    @inject
    async def _inner(
        value: Resources = Provide[provider],
    ) -> None:
        assert provider.initialized
        assert provider._context is not None

        assert value.active
        assert not value.closed

    await _inner()

    assert provider.initialized
    assert provider._context is not None

    assert provider.instance.active
    assert not provider.instance.closed


async def test_resource_function_scope_async(container: Type[Container]) -> None:
    provider = container.async_resource_func_scope

    @inject
    async def _inner(
        value: Resources = Provide[provider],
    ) -> None:
        assert provider.initialized
        assert provider._context is not None

        assert value.active
        assert not value.closed

    await _inner()

    assert not provider.initialized
    assert provider._context is None

    assert not provider.instance.active
    assert provider.instance.closed


def test_resource_provider_fail_with_unsupported_factory() -> None:
    with pytest.raises(RuntimeError, match="Unsupported resource factory type"):
        Resource(lambda: None)  # type: ignore[arg-type,return-value]


async def test_resource_provider_inject_async_resource_to_sync_function(
    container: Type[Container],
) -> None:
    value = await container.sync_func_with_async_resource_dependency.async_resolve()

    assert isinstance(value, Resources)
    assert value.active
    assert not value.closed


def test_resource_provider_based_on_ctx_manager_class() -> None:
    class _CtxManager(ContextManager[int]):
        def __enter__(self) -> int:
            return 2

        def __exit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc_value: Optional[BaseException],
            traceback: Optional[TracebackType],
        ) -> None:
            return None

    provider = Resource(_CtxManager)

    assert provider() == 2


async def test_resource_provider_based_on_async_ctx_manager_class() -> None:
    class _AsyncCtxManager(AsyncContextManager[int]):
        async def __aenter__(self) -> int:
            return 2

        async def __aexit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc_value: Optional[BaseException],
            traceback: Optional[TracebackType],
        ) -> None:
            return None

    provider = Resource(_AsyncCtxManager)

    assert await provider.async_resolve() == 2
