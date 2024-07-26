# Singleton

Singleton provider make caching for your object.
sfsfsfdf

## Example

```python3
from injection import DeclarativeContainer, providers


class SingletonClass:
    field: int


class DIContainer(DeclarativeContainer):
    singleton_provider = providers.Singleton(SingletonClass, field=15)


if __name__ == "__main__":
    instance1 = DIContainer.singleton_provider()
    instance2 = DIContainer.singleton_provider()

    assert instance1 is instance2
    assert instance1.field == 15
```
