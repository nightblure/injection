import asyncio
from dataclasses import dataclass
from typing import Tuple

import pytest

from injection import providers


async def _coroutine(arg1: int, arg2: int) -> Tuple[int, int]:
    return arg1, arg2


async def test_coroutine_provider_direct_resolve() -> None:
    async_factory_provider = providers.Transient(_coroutine, arg1=1, arg2=2)
    result = await async_factory_provider.async_resolve()

    assert result == (1, 2)  # type: ignore[comparison-overlap]


def test_async_factory_provider_event_loop_resolve() -> None:
    async_factory_provider = providers.Transient(_coroutine, arg1=1, arg2=2)
    coro = async_factory_provider.async_resolve()

    result = asyncio.run(coro)

    assert result == (1, 2)  # type: ignore[comparison-overlap]


@dataclass
class SomeClass:
    field1: str
    field2: int


@pytest.fixture
def transient_provider() -> providers.Transient[SomeClass]:
    return providers.Transient(SomeClass, field1="value", field2=1)


def test_transient_provider_override_args(
    transient_provider: providers.Transient[SomeClass],
) -> None:
    resolved = transient_provider(field1="new_value", field2=100)

    assert resolved.field1 == "new_value"
    assert resolved.field2 == 100

    resolved = transient_provider()
    assert resolved.field1 == "value"
    assert resolved.field2 == 1


def test_reset_override_no_fail_when_no_mocks(
    transient_provider: providers.Transient[SomeClass],
) -> None:
    transient_provider.reset_override()
    transient_provider.reset_override()
