# Factory

**Factory** works exactly same as **Transient** provider.

Also supports **asynchronous** dependencies.

## Example

```python3
import asyncio
from dataclasses import dataclass
from typing import Tuple

from injection import DeclarativeContainer, providers


@dataclass
class SomeClass:
    field: Tuple[int, int]


async def coroutine_func(arg1: int, arg2: int) -> Tuple[int, int]:
    return arg1, arg2


class DIContainer(DeclarativeContainer):
    coroutine = providers.Coroutine(coroutine_func, arg1=1, arg2=2)
    sync_factory = providers.Factory(SomeClass, field=(10, 20))
    async_factory = providers.Factory(SomeClass, field=coroutine)


async def main() -> None:
    instance = await DIContainer.async_factory.async_resolve()
    assert instance.field == (1, 2)


instance1 = DIContainer.sync_factory()
instance2 = DIContainer.sync_factory()
assert instance1 is not instance2

asyncio.run(main())
```
