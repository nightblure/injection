# Provided instance

You can pass provider field values to other providers,
which will provide dependency injection.
To access the values of an object's fields inside a provider,
you need to use the `provided` property of the provider.

This is useful in cases when your entities depend on external data
from configuration files or environment variables.
You need to parse this external data and save it into a class or dataclass,
and the container will inject this data.

### Example
```python3
from dataclasses import dataclass

from injection import DeclarativeContainer, providers


@dataclass
class Settings:
    env_1: str
    env_2: int


class SomeService:
    def __init__(self, env_1: str, env_2: int):
        self.env_1 = env_1
        self.env_2 = env_2


class Container(DeclarativeContainer):
    settings = providers.Singleton(Settings, env_1="value", env_2=193)

    service = providers.Transient(
        SomeService,
        env_1=settings.provided.env_1,
        env_2=settings.provided.env_2,
    )


if __name__ == "__main__":
    resolved_service = Container.service()
    assert resolved_service.env_1 == "value"
    assert resolved_service.env_2 == 193
```
