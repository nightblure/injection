# Auto injection

**Auto injection** allows you to **not specify markers and providers** 
in the parameters of the function for which you want to inject dependencies. 

Here it is enough to **specify** the **types** for which the corresponding providers
have already been created in the container.
`@autoinject` decorator will try to find providers according to the types 
of the function parameters and inject the dependencies.

### Usage with multiple containers

The `@autoinject` decorator can take a `target_container` **parameter**. 
You can omit the container if you have only one in your code, 
but you must if you have several in your code.

### Example

```python
from injection import DeclarativeContainer, auto_inject, providers


class SomeClass:
    def __init__(self, a: int, b: str) -> None:
        self.a = a
        self.b = b

    def func(self) -> str:
        return "sync func"

    async def async_func(self) -> str:
        return "async func"


class DIContainer(DeclarativeContainer):
    some_provider = providers.Factory(SomeClass, a=1, b="b")


def test_auto_inject_to_sync_function() -> None:
    @auto_inject(target_container=DIContainer)
    def _sync_func(obj: SomeClass) -> None:
        assert obj.func() == "sync func"
        assert obj.a == 1
        assert obj.b == "b"

    _sync_func()


async def test_auto_inject_to_async_function() -> None:
    # It is not necessary to pass target_container if there is only one
    @auto_inject()
    async def _async_func(obj: SomeClass) -> None:
        assert await obj.async_func() == "async func"
        assert obj.a == 1
        assert obj.b == "b"

    await _async_func()
```
