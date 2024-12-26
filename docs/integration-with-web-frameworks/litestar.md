# Litestar

In order to successfully inject dependencies into Litestar request handlers,
make sure that the following points are completed:
1. use `@inject` decorator **before** http-method `Litestar` decorator;

2. added for each injected parameter to the request handler a typing of the form
`Annotated[<your type>, Dependency(skip_validation=True)]`. `Dependency` is object from `litestar.params`;

3. use the `Provide` marker from the `injection` (_not from Litestar_) package indicating the provider

---

## Example

```python3
from functools import partial
from random import Random
from typing import Any, Dict
from unittest.mock import Mock

import pytest
from litestar import Litestar, get
from litestar.params import Dependency
from litestar.testing import TestClient
from typing_extensions import Annotated

from injection import DeclarativeContainer, Provide, inject, providers

_NoValidationDependency = partial(Dependency, skip_validation=True)


class Redis:
    def __init__(self, *, url: str, port: int):
        self.uri = url + ":" + str(port)
        self.url = url
        self.port = port

    def get(self, key: Any) -> Any:
        return key


class Container(DeclarativeContainer):
    redis = providers.Singleton(
        Redis,
        port=9873,
        url="redis://...",
    )
    num = providers.Object(9402)


@get(
    "/some_resource/{redis_key:int}",
    status_code=200,
)
@inject
async def litestar_endpoint(
    redis_key: int,
    num: Annotated[int, _NoValidationDependency()] = Provide[Container.num],
    redis: Annotated[Redis, _NoValidationDependency()] = Provide[Container.redis],
) -> Dict[str, Any]:
    value = redis.get(redis_key)
    return {"key": value, "num2": num}


@get(
    "/num_endpoint",
    status_code=200,
)
@inject
async def litestar_endpoint_object_provider(
    num: Annotated[int, _NoValidationDependency()] = Provide[Container.num],
) -> Dict[str, Any]:
    return {"detail": num}


_handlers = [
    litestar_endpoint,
    litestar_endpoint_object_provider,
]

app = Litestar(route_handlers=_handlers)


##################################################### TESTS ############################################################
@pytest.fixture(scope="session")
def test_client() -> TestClient[Any]:
    return TestClient(app=app)


def test_num_endpoint(test_client: TestClient[Any]) -> None:
    response = test_client.get("/num_endpoint")

    assert response.status_code == 200
    assert response.json() == {"detail": 9402}


def test_some_resource_endpoint(test_client: TestClient[Any]) -> None:
    key = Random().randint(0, 100)  # noqa: S311

    response = test_client.get(f"/some_resource/{key}")

    assert response.status_code == 200
    assert response.json() == {"key": key, "num2": 9402}


def test_overriding(test_client: TestClient[Any]) -> None:
    key = 192342526
    mock_instance = Mock(get=lambda _: key)
    override_providers = {"redis": mock_instance, "num": -2999999999}

    with Container.override_providers(override_providers):
        response = test_client.get(f"/some_resource/{key}")

    assert response.status_code == 200
    assert response.json() == {"key": key, "num2": -2999999999}

```
