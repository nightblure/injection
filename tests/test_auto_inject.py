from typing import Any, Iterator, List, Tuple
from unittest import mock

import pytest

from injection import DeclarativeContainer, Provide, auto_inject, providers
from injection.exceptions import (
    DuplicatedFactoryTypeAutoInjectionError,
    UnknownProviderTypeAutoInjectionError,
)


class Service:
    def __init__(self, a: int = 1, *, b: str = "b") -> None:
        self.a = a
        self.b = b

    def func(self) -> str:
        return "sync func"

    async def async_func(self) -> str:
        return "async func"


class Resources:
    def __init__(self, a: int, *, b: str) -> None:
        self.a = a
        self.b = b
        self.active = False

    def __enter__(self) -> "Resources":
        self.active = True
        return self

    def __exit__(self, *args: Any) -> None:
        self.active = False

    async def __aenter__(self) -> "Resources":
        self.active = True
        return self

    async def __aexit__(self, *args: Any) -> None:
        self.active = False


class Container(DeclarativeContainer):
    service = providers.Factory(Service)
    func_scope_resource = providers.Resource(
        Resources,
        a=1199,
        b="bbbb",
        function_scope=True,
    )


@pytest.mark.parametrize(
    "subclasses",
    [
        [object(), object()],
        [object(), object(), object()],
    ],
)
def test_auto_inject_expect_error_with_more_than_one_di_container_and_empty_target_container_param(
    subclasses: List[Any],
) -> None:
    match = (
        f"Found {len(subclasses)} containers, "
        f"please specify the required container explicitly in the parameter 'target_container'"
    )

    with mock.patch.object(
        DeclarativeContainer,
        "__subclasses__",
        return_value=subclasses,
    ):
        with pytest.raises(Exception, match=match):
            auto_inject()(lambda: None)


async def test_auto_inject_expect_error_on_duplicated_provider_types() -> None:
    @auto_inject(target_container=Container)
    async def _async_func(a: Any, b: Any, _: Service) -> Tuple[Any, Any]:
        return a, b

    _mock_providers = [Container.__dict__["service"]]
    _mock_providers.extend(
        Container.get_providers(),
    )

    with mock.patch.object(
        Container,
        "get_providers",
        return_value=_mock_providers,
    ):
        with pytest.raises(DuplicatedFactoryTypeAutoInjectionError):
            await _async_func(a=234, b="rnd")  # type: ignore[call-arg]


def test_auto_injection_with_args_overriding() -> None:
    @auto_inject(target_container=Container)
    def _inner(
        arg1: bool,  # noqa: FBT001
        arg2: Service,
        arg3: int = 100,
    ) -> None:
        _ = arg1
        _ = arg3
        original_obj = Container.service()
        assert arg2.a != original_obj.a
        assert arg2.b != original_obj.b

    _inner(True, Container.service(b="url", a=2000))  # noqa: FBT003
    _inner(arg1=True, arg2=Container.service(b="urljyfuf", a=8400))
    _inner(True, arg2=Container.service(b="afdsfsf", a=2242))  # noqa: FBT003


async def test_auto_injection_with_args_overriding_async() -> None:
    @auto_inject(target_container=Container)
    async def _inner(
        arg1: bool,  # noqa: FBT001
        arg2: Service,
        arg3: int = 100,
    ) -> int:
        _ = arg1
        _ = arg3
        original_obj = Container.service()
        assert arg2.a != original_obj.a
        assert arg2.b != original_obj.b
        return arg3

    assert await _inner(True, Container.service(b="url", a=2000)) == 100  # noqa: FBT003
    assert await _inner(arg1=True, arg2=Container.service(b="url", a=2000)) == 100
    assert await _inner(True, arg2=Container.service(b="url", a=2000)) == 100  # noqa: FBT003


def test_auto_injection_expect_error_on_unknown_provider() -> None:
    @auto_inject(target_container=Container)
    def inner(_: object) -> Any: ...

    with pytest.raises(UnknownProviderTypeAutoInjectionError):
        inner()  # type: ignore[call-arg]


async def test_auto_injection_expect_error_on_unknown_provider_async() -> None:
    @auto_inject(target_container=Container)
    async def inner(_: object) -> Any: ...

    with pytest.raises(UnknownProviderTypeAutoInjectionError):
        await inner()  # type: ignore[call-arg]


def test_auto_inject_to_sync_function() -> None:
    @auto_inject(target_container=Container)
    def _sync_func(obj: Service) -> None:
        assert obj.func() == "sync func"
        assert obj.a == 1
        assert obj.b == "b"

    _sync_func()  # type: ignore[call-arg]


async def test_auto_inject_to_async_function() -> None:
    @auto_inject(target_container=Container)
    async def _async_func(obj: Service) -> None:
        assert await obj.async_func() == "async func"
        assert obj.a == 1
        assert obj.b == "b"

    await _async_func()  # type: ignore[call-arg]


def test_auto_inject_with_func_scope_resource() -> None:
    provider = Container.func_scope_resource

    @auto_inject(target_container=Container)
    def _sync_func(obj: Service, resource: Resources) -> Resources:
        assert obj.func() == "sync func"
        assert resource.a == 1199
        assert resource.b == "bbbb"
        assert resource.active
        assert provider.initialized
        assert provider.instance is resource
        return resource

    resource_obj = _sync_func()  # type: ignore[call-arg]

    assert not resource_obj.active
    assert not provider.initialized
    assert provider.instance is None


async def test_auto_inject_with_async_func_scope_resource() -> None:
    class _Container(DeclarativeContainer):
        service = providers.Factory(Service)
        async_func_scope_resource = providers.Resource(
            Resources,
            a=1199,
            b="bbbb",
            function_scope=True,
        )

    provider = _Container.async_func_scope_resource

    @auto_inject(target_container=_Container)
    async def _async_func(obj: Service, resource: Resources) -> Resources:
        assert await obj.async_func() == "async func"
        assert resource.a == 1199
        assert resource.b == "bbbb"
        assert resource.active
        assert provider.initialized
        assert provider.instance is resource
        return resource

    resource_obj = await _async_func()  # type: ignore[call-arg]

    assert not resource_obj.active
    assert not provider.initialized
    assert provider.instance is None


async def test_auto_inject_mixed_async() -> None:
    def _sync_resource(a: int) -> Iterator[int]:
        yield a

    class ResourceAsync(Resources): ...

    class _Container(DeclarativeContainer):
        service = providers.Factory(Service)
        async_func_scope_resource = providers.Resource(
            Resources,
            a=1199,
            b="bbbb",
            function_scope=True,
        )
        async_resource_copy = providers.Resource(
            ResourceAsync,
            a=1199,
            b="bbbb",
            function_scope=False,
        )
        func_scope_resource = providers.Resource(
            _sync_resource,
            a=-99,
            function_scope=True,
        )

    provider = _Container.async_func_scope_resource

    @auto_inject(target_container=_Container)
    async def _async_func(
        resource: Resources,
        obj: Service = Provide[_Container.service],
        func_scope_res_value: int = Provide[_Container.func_scope_resource],
        _: Resources = Provide[_Container.async_resource_copy],
        num: int = Provide[providers.Object(100)],
    ) -> Resources:
        assert num == 100
        assert func_scope_res_value == -99
        assert await obj.async_func() == "async func"
        assert resource.a == 1199
        assert resource.b == "bbbb"
        assert resource.active
        assert provider.initialized
        assert provider.instance is resource

        assert _Container.async_resource_copy.initialized
        return resource

    resource_obj = await _async_func()  # type: ignore[call-arg]

    assert not resource_obj.active
    assert not provider.initialized
    assert provider.instance is None
    assert _Container.async_resource_copy.initialized


async def test_auto_inject_mixed_sync() -> None:
    class ResourceCopy(Resources): ...

    class _Container(DeclarativeContainer):
        service = providers.Factory(Service)
        func_scope_resource = providers.Resource(
            Resources,
            a=1199,
            b="bbbb",
            function_scope=True,
        )
        sync_resource_copy = providers.Resource(
            ResourceCopy,
            a=1199,
            b="bbbb",
            function_scope=False,
        )

    provider = _Container.func_scope_resource

    @auto_inject(target_container=_Container)
    def _func(
        resource: Resources,
        obj: Service = Provide[_Container.service],
        _: Resources = Provide[_Container.sync_resource_copy],
        num: int = Provide[providers.Object(100)],
    ) -> Resources:
        assert num == 100
        assert obj.func() == "sync func"
        assert resource.a == 1199
        assert resource.b == "bbbb"
        assert resource.active
        assert provider.initialized
        assert provider.instance is resource

        assert _Container.sync_resource_copy.initialized
        return resource

    resource_obj = _func()  # type: ignore[call-arg]

    assert not resource_obj.active
    assert not provider.initialized
    assert provider.instance is None
    assert _Container.sync_resource_copy.initialized
