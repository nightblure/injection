# Resource

**Resource provider** provides a component with **initialization** and **closing**.
**Resource providers** supports next **initializers**:
* **sync** and **async** **generators**;
* **inheritors** of `ContextManager` and `AsyncContextManager` classes;
* functions wrapped into `@contextmanager` and `@asynccontextmanager` **decorators**.

## Working scope
Resource provider can works with two scopes: **singleton** and **function-scope**.

**Function-scope** requires to set parameter of `Resource` provider `function_scope=True`.
**Function-scope** resources can works only with `@inject` decorator!

## Example
```python
from typing import Tuple, Iterator, AsyncIterator

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
        async_func_scope_value: str = Provide[DIContainer.async_resource_func_scope]
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


if __name__ == "__main__":
    await main()
```
