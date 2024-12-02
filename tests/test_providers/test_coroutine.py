import asyncio
from typing import Any, Tuple, Type
from unittest.mock import Mock

import pytest

from injection import Provide, inject
from tests.container_objects import Container


@pytest.mark.asyncio
async def test_coroutine_provider_direct_resolve(container: Type[Container]) -> None:
    result = await container.coroutine_provider.async_resolve()

    assert result == (1, 2)


def test_coroutine_provider_event_loop_resolve(container: Type[Container]) -> None:
    coro = container.coroutine_provider.async_resolve()

    result = asyncio.run(coro)

    assert result == (1, 2)


def test_coroutine_provider_error_on_sync_resolving(container: Type[Container]) -> None:
    with pytest.raises(
        RuntimeError,
        match="Coroutine provider cannot be resolved synchronously",
    ):
        container.coroutine_provider()


async def test_coroutine_provider_injection(container: Type[Container]) -> None:
    @inject
    async def _inner(
        coro_value: Tuple[int, int] = Provide[container.coroutine_provider],
    ) -> None:
        assert coro_value == (1, 2)

    await _inner()


async def test_coroutine_nested_async_injections(container: Type[Container]) -> None:
    @inject
    async def _inner(
        value: Tuple[Tuple[int, int], Tuple[int, int], int] = Provide[
            container.nested_coro_provider
        ],
    ) -> None:
        assert value == ((1, 2), (1, 2), 144)

    await _inner()


async def test_coroutine_provider_chained_injection(container: Type[Container]) -> None:
    @inject
    async def _inner(
        param: Tuple[
            int,
            Tuple[int, int],
            Tuple[int, int],
            Tuple[
                Tuple[int, int],
                Tuple[int, int],
                int,
            ],
        ] = Provide[container.async_dependency_provider],
    ) -> None:
        assert param == (
            1778,
            (1, 2),
            (1, 2),
            (
                (1, 2),
                (1, 2),
                144,
            ),
        )

    await _inner()


async def test_coroutine_provider_injecting_to_sync_function(
    container: Type[Container],
) -> None:
    value = await container.sync_func_with_coro_dependency.async_resolve()

    assert value == (1, 2)  # type: ignore[comparison-overlap]


async def test_coroutine_provider_overriding(container: Type[Container]) -> None:
    @inject
    async def _inner(
        v: Any = Provide[container.coroutine_provider],
    ) -> str:
        return v()  # type: ignore[no-any-return]

    with container.coroutine_provider.override_context(Mock(return_value="mock")):
        value = await _inner()

    assert value == "mock"
