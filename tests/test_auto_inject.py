from unittest import mock

import pytest

from injection import DeclarativeContainer, auto_inject
from injection.inject.exceptions import DuplicatedFactoryTypeAutoInjectionError
from tests.container_objects import Redis, Service, SomeService


@pytest.mark.parametrize(
    "subclasses",
    [
        [object(), object()],
        [object(), object(), object()],
    ],
)
def test_auto_inject_expect_error_with_more_than_one_di_container_and_empty_target_container_param(
    subclasses: list,
):
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
            auto_inject(lambda: None)


@auto_inject
async def _async_func(
    redis: Redis,
    *,
    a: int,
    b: str = "asdsd",
    svc: Service,
    another_svc: SomeService,
):
    assert a == 234
    assert b == "rnd"
    assert isinstance(redis, Redis)
    assert isinstance(svc, Service)
    assert isinstance(another_svc, SomeService)


async def test_auto_inject_on_async_target():
    await _async_func(a=234, b="rnd")


async def test_auto_inject_expect_error_on_duplicated_provider_types(container):
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
            await _async_func(a=234, b="rnd")
