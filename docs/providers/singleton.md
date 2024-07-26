# Singleton

**Singleton** provider creates and returns a new object on the first call
and caches it, and on subsequent calls it returns the cached object.

## Example

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
