# Object

**Object** provider returns an object “as is”.

## Example

```python3
from injection import DeclarativeContainer, providers


class Container(DeclarativeContainer):
    provider1 = providers.Object("string")
    provider2 = providers.Object(13425)


if __name__ == "__main__":
    assert Container.provider1() == "string"
    assert Container.provider2() == 13425


```
