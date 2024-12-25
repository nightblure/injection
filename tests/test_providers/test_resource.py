from types import TracebackType
from typing import (
    Any,
    AsyncContextManager,
    AsyncIterator,
    ContextManager,
    Iterator,
    Optional,
    Type,
)
from unittest.mock import Mock

import pytest

from injection import DeclarativeContainer, Provide, inject, providers
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

    assert provider.instance is not None
    assert provider.instance.active
    assert not provider.instance.closed


def test_resource_function_scope(container: Type[Container]) -> None:
    provider = container.sync_resource_func_scope

    @inject
    def _inner(
        value: Resources = Provide[provider],
    ) -> Resources:
        assert provider.initialized
        assert provider._context is not None

        assert value.active
        assert not value.closed
        return value

    instance = _inner()

    assert not provider.initialized
    assert provider._context is None
    assert provider.instance is None

    assert not instance.active
    assert instance.closed


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

    assert provider.instance is not None
    assert provider.instance.active
    assert not provider.instance.closed


async def test_resource_function_scope_async(container: Type[Container]) -> None:
    provider = container.async_resource_func_scope

    @inject
    async def _inner(
        value: Resources = Provide[provider],
    ) -> Resources:
        assert provider.initialized
        assert provider._context is not None

        assert value.active
        assert not value.closed
        return value

    instance = await _inner()

    assert not provider.initialized
    assert provider._context is None
    assert provider.instance is None

    assert not instance.active
    assert instance.closed


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


def test_resource_provider_overriding(container: Type[Container]) -> None:
    @inject
    def _inner(
        v: Any = Provide[container.sync_resource],
    ) -> str:
        return v()  # type: ignore[no-any-return]

    with container.sync_resource.override_context(Mock(return_value="mock")):
        value = _inner()

    assert value == "mock"


async def test_resource_provider_overriding_with_async_func_and_sync_resource(
    container: Type[Container],
) -> None:
    @inject
    async def _inner(
        v: Any = Provide[container.sync_resource],
    ) -> str:
        return v()  # type: ignore[no-any-return]

    with container.sync_resource.override_context(Mock(return_value="mock")):
        value = await _inner()

    assert value == "mock"


async def test_resource_provider_overriding_with_async_func_and_async_resource(
    container: Type[Container],
) -> None:
    @inject
    async def _inner(
        v: Any = Provide[container.async_resource],
    ) -> str:
        return v()  # type: ignore[no-any-return]

    with container.async_resource.override_context(Mock(return_value="mock")):
        value = await _inner()

    assert value == "mock"


def test_resource_provider_closing_expect_error_when_not_initialized(
    container: Type[Container],
) -> None:
    with pytest.raises(RuntimeError, match="Resource is not initialized"):
        container.sync_resource.close()


async def test_resource_provider_async_closing_expect_error_when_not_initialized(
    container: Type[Container],
) -> None:
    with pytest.raises(RuntimeError, match="Resource is not initialized"):
        await container.async_resource.async_close()


def test_resource_provider_successful_repeat_resolving(
    container: Type[Container],
) -> None:
    container.init_resources()

    assert isinstance(container.sync_resource(), Resources)


async def test_resource_provider_successful_repeat_async_resolving(
    container: Type[Container],
) -> None:
    await container.init_resources_async()

    value = await container.async_resource.async_resolve()

    assert isinstance(value, Resources)


async def test_resource_provider_docs_code() -> None:
    from typing import AsyncIterator, Iterator, Tuple

    from injection import DeclarativeContainer, Provide, inject, providers

    def sync_func() -> Iterator[str]:
        yield "sync_func"

    async def async_func() -> AsyncIterator[str]:
        yield "async_func"

    class DIContainer(DeclarativeContainer):
        sync_resource = providers.Resource(sync_func)
        async_resource = providers.Resource(async_func)

        sync_resource_func_scope = providers.Resource(sync_func, function_scope=True)
        async_resource_func_scope = providers.Resource(async_func, function_scope=True)

    @inject
    async def func_with_injections(
        sync_value: str = Provide[DIContainer.sync_resource],
        async_value: str = Provide[DIContainer.async_resource],
        sync_func_scope_value: str = Provide[DIContainer.sync_resource_func_scope],
        async_func_scope_value: str = Provide[DIContainer.async_resource_func_scope],
    ) -> Tuple[str, str, str, str]:
        return sync_value, async_value, sync_func_scope_value, async_func_scope_value

    async def main() -> None:
        values = await func_with_injections()

        assert values == ("sync_func", "async_func", "sync_func", "async_func")

        assert DIContainer.sync_resource.initialized
        assert DIContainer.async_resource.initialized

        # Resources with function scope were closed after dependency injection
        assert not DIContainer.sync_resource_func_scope.initialized
        assert not DIContainer.async_resource_func_scope.initialized

    await main()


def test_related_resource_providers_closing_sync() -> None:
    def sync_func(val: str) -> Iterator[str]:
        yield val

    class _Container(DeclarativeContainer):
        resource = providers.Resource(sync_func, "resource lvl 1")
        resource_func_scope = providers.Resource(
            sync_func,
            resource,
            function_scope=True,
        )
        resource_func_scope_2 = providers.Resource(
            sync_func,
            resource_func_scope,
            function_scope=True,
        )

        unrelated_resource = providers.Resource(
            sync_func,
            "no matter",
            function_scope=True,
        )

    @inject
    def func(v: str = Provide[_Container.resource_func_scope_2]) -> None:
        assert _Container.resource.initialized
        assert _Container.resource.instance is not None

        assert v == "resource lvl 1"
        for p in [_Container.resource_func_scope, _Container.resource_func_scope_2]:
            assert p.initialized
            assert p.instance == "resource lvl 1"

        assert not _Container.unrelated_resource.initialized
        assert _Container.unrelated_resource.instance is None

    func()

    assert _Container.resource.initialized
    assert _Container.resource.instance is not None

    for provider in [_Container.resource_func_scope, _Container.resource_func_scope_2]:
        assert not provider.initialized
        assert provider.instance is None

    assert not _Container.unrelated_resource.initialized
    assert _Container.unrelated_resource.instance is None


async def test_related_resource_providers_closing_async() -> None:
    async def func(val: str) -> AsyncIterator[str]:
        yield val

    class _Container(DeclarativeContainer):
        resource = providers.Resource(func, "resource lvl 1")
        resource_func_scope = providers.Resource(func, resource, function_scope=True)
        resource_func_scope_2 = providers.Resource(
            func,
            resource_func_scope,
            function_scope=True,
        )

        unrelated_resource = providers.Resource(func, "no matter", function_scope=True)

    @inject
    async def func_with_injections(
        v: str = Provide[_Container.resource_func_scope_2],
    ) -> None:
        assert _Container.resource.initialized
        assert _Container.resource.instance is not None

        assert v == "resource lvl 1"
        for p in [_Container.resource_func_scope, _Container.resource_func_scope_2]:
            assert p.initialized
            assert p.instance == "resource lvl 1"

        assert not _Container.unrelated_resource.initialized
        assert _Container.unrelated_resource.instance is None

    await func_with_injections()

    assert _Container.resource.initialized
    assert _Container.resource.instance is not None

    for provider in [_Container.resource_func_scope, _Container.resource_func_scope_2]:
        assert not provider.initialized
        assert provider.instance is None

    assert not _Container.unrelated_resource.initialized
    assert _Container.unrelated_resource.instance is None
