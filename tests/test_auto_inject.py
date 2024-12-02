from typing import Any, List, Type
from unittest import mock

import pytest

from injection import DeclarativeContainer, auto_inject
from injection.inject.exceptions import (
    DuplicatedFactoryTypeAutoInjectionError,
    UnknownProviderTypeAutoInjectionError,
)
from tests.container_objects import Container, Redis, Service, SomeService


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


@auto_inject(target_container=Container)
async def _async_func(
    redis: Redis,
    *,
    a: int,
    b: str = "asdsd",
    svc: Service,
    another_svc: SomeService,
) -> None:
    assert a == 234
    assert b == "rnd"
    assert isinstance(redis, Redis)
    assert isinstance(svc, Service)
    assert isinstance(another_svc, SomeService)


async def test_auto_inject_on_async_target() -> None:
    await _async_func(a=234, b="rnd")  # type: ignore[call-arg]


async def test_auto_inject_expect_error_on_duplicated_provider_types(
    container: Type[Container],
) -> None:
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
            await _async_func(a=234, b="rnd")  # type: ignore[call-arg]


def test_auto_injection_with_args_overriding(container: Type[Container]) -> None:
    @auto_inject(target_container=Container)
    def _inner(
        arg1: bool,  # noqa: FBT001
        arg2: Service,
        arg3: int = 100,
    ) -> None:
        _ = arg1
        _ = arg3
        original_obj = container.service()
        assert arg2.a != original_obj.a
        assert arg2.b != original_obj.b

    _inner(True, container.service(b="url", a=2000))  # noqa: FBT003
    _inner(arg1=True, arg2=container.service(b="urljyfuf", a=8400))
    _inner(True, arg2=container.service(b="afdsfsf", a=2242))  # noqa: FBT003


async def test_auto_injection_with_args_overriding_async(
    container: Type[Container],
) -> None:
    @auto_inject(target_container=Container)
    async def _inner(
        arg1: bool,  # noqa: FBT001
        arg2: Service,
        arg3: int = 100,
    ) -> int:
        _ = arg1
        _ = arg3
        original_obj = container.service()
        assert arg2.a != original_obj.a
        assert arg2.b != original_obj.b
        return arg3

    assert await _inner(True, container.service(b="url", a=2000)) == 100  # noqa: FBT003
    assert await _inner(arg1=True, arg2=container.service(b="url", a=2000)) == 100
    assert await _inner(True, arg2=container.service(b="url", a=2000)) == 100  # noqa: FBT003


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
