# Coroutine

**Coroutine** provider creates a coroutine.

## Example

```python3
import asyncio

from injection import DeclarativeContainer, providers


async def coroutine(arg1, arg2):
    await asyncio.sleep(0.1)
    return arg1, arg2


class DIContainer(DeclarativeContainer):
    provider = providers.Coroutine(coroutine, arg1=1, arg2=2)


if __name__ == "__main__":
    arg1, arg2 = asyncio.run(DIContainer.provider())
    assert (arg1, arg2) == (1, 2)
```
