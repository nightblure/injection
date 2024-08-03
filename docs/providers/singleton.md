# Singleton

**Singleton** provider creates and returns a new object on the first call
and caches it, and on subsequent calls it returns the cached object.

### Example

```python3
from dataclasses import dataclass

from injection import DeclarativeContainer, providers


@dataclass
class SingletonClass:
    field: int


class DIContainer(DeclarativeContainer):
    provider = providers.Singleton(SingletonClass, field=15)


if __name__ == "__main__":
    instance1 = DIContainer.provider()
    instance2 = DIContainer.provider()

    assert instance1 is instance2
    assert instance1.field == 15

```

## Resetting memoized object

To **reset a memorized object** you need to call the `reset` method of the Singleton provider.

### Example

```python3
from injection import DeclarativeContainer, providers


class SomeClass: ...


if __name__ == "__main__":
    provider = providers.Singleton(SomeClass)
    obj = provider()
    obj2 = provider()

    assert obj is obj2
    provider.reset()

    obj3 = provider()
    assert obj is not obj3
    assert obj2 is not obj3
```
