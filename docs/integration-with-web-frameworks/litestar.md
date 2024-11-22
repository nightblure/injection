# Using with Litestar

In order to successfully inject dependencies into Litestar request handlers,
make sure that the following points are completed:
1. use `@inject` decorator **before** http-method `Litestar` decorator;

2. added for each injected parameter to the request handler a typing of the form
`Annotated[<your type>, Dependency(skip_validation=True)]`. `Dependency` is object from `litestar.params`;

3. use the `Provide` marker from the `injection` (not from Litestar) package indicating the provider

---

## Example

```python3
from functools import partial
from unittest.mock import Mock
from typing import Annotated

from injection import Provide, inject, DeclarativeContainer, providers
from litestar import Litestar, get
from litestar.params import Dependency
from litestar.testing import TestClient


_NoValidationDependency = partial(Dependency, skip_validation=True)


class Redis:
    def __init__(self, *, url: str, port: int):
        self.uri = url + ":" + str(port)
        self.url = url
        self.port = port

    def get(self, key):
        return key


class Container(DeclarativeContainer):
    redis = providers.Singleton(
        Redis,
        port=9873,
        url="redis://...",
    )
    num = providers.Object(9402)


@get(
    "/some_resource",
    status_code=200,
)
@inject
async def litestar_endpoint(
    num: Annotated[int, _NoValidationDependency()] = Provide[Container.num],
    redis: Annotated[Redis, _NoValidationDependency()] = Provide[Container.redis],
) -> dict:
    value = redis.get(800)
    return {"detail": value, "num2": num}


@get(
    "/num_endpoint",
    status_code=200,
)
@inject
async def litestar_endpoint_object_provider(
    num: Annotated[int, _NoValidationDependency()] = Provide[Container.num],
) -> dict:
    return {"detail": num}


_handlers = [
    litestar_endpoint,
    litestar_endpoint_object_provider,
]

app = Litestar(route_handlers=_handlers)

# Testing

def test_litestar_overriding():
    mock_instance = Mock(get=lambda _: 192342526)
    override_providers = {"redis": mock_instance, "num": -2999999999}

    with TestClient(app=app) as client:
        with Container.override_providers(override_providers):
            response = client.get("/some_resource")

    assert response.status_code == 200
    assert response.json() == {"detail": 192342526, "num2": -2999999999}

```
