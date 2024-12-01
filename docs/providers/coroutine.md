# Coroutine

**Coroutine** provider creates a coroutine.
Can be resolved only with using the `async_resolve` method.

## Example

```python3
    import asyncio
    from typing import Tuple

    from injection import DeclarativeContainer, providers

    async def coroutine(arg1: int, arg2: int) -> Tuple[int, int]:
        return arg1, arg2

    class DIContainer(DeclarativeContainer):
        provider = providers.Coroutine(coroutine, arg1=1, arg2=2)

    arg1, arg2 = asyncio.run(DIContainer.provider.async_resolve())
    assert (arg1, arg2) == (1, 2)

    async def main() -> None:
        arg1, arg2 = await DIContainer.provider.async_resolve(arg1=500, arg2=600)
        assert (arg1, arg2) == (500, 600)

    asyncio.run(main())
```
