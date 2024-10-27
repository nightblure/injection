import asyncio

import pytest

from injection import providers


async def coroutine(arg1, arg2):
    await asyncio.sleep(0.1)
    return arg1, arg2


@pytest.mark.asyncio
async def test_coroutine_provider_direct_resolve():
    coroutine_provider = providers.Coroutine(coroutine, arg1=1, arg2=2)
    coro = coroutine_provider()
    result = await coro
    assert result == (1, 2)


def test_coroutine_provider_event_loop_resolve():
    coroutine_provider = providers.Coroutine(coroutine, arg1=1, arg2=2)
    coro = coroutine_provider()
    result = asyncio.run(coro)
    assert result == (1, 2)
