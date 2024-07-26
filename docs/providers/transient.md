# Transient

**Transient** provider creates and returns a new object for each call.

## Example

```python3
from dataclasses import dataclass

from injection import DeclarativeContainer, providers


@dataclass
class SomeClass:
    field: str


class DIContainer(DeclarativeContainer):
    provider = providers.Transient(SomeClass, field="str_value")


if __name__ == "__main__":
    instance1 = DIContainer.provider()
    instance2 = DIContainer.provider()

    assert instance1 is not instance2

```
