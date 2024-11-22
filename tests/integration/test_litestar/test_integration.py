import sys
from functools import partial
from typing import Any, Union
from unittest.mock import Mock

import pytest
from litestar import Controller, Litestar, get
from litestar.params import Dependency
from litestar.testing import TestClient

from injection import Provide, inject
from tests.container_objects import Container, Redis

if sys.version_info >= (3, 9):
    from typing import Annotated
else:
    from typing_extensions import Annotated

_NoValidationDependency = partial(Dependency, skip_validation=True)


@get(
    "/some_resource",
    status_code=200,
)
@inject
async def litestar_endpoint(
    redis: Annotated[Redis, _NoValidationDependency()] = Provide[Container.redis],
    num: Annotated[int, _NoValidationDependency()] = Provide[Container.num2],
) -> dict:
    value = redis.get(800)
    return {"detail": value, "num2": num}


@get(
    "/num_endpoint",
    status_code=200,
)
@inject
async def litestar_endpoint_object_provider(
    num: Union[int, Any] = Provide[Container.num2],
) -> dict:
    return {"detail": num}


class LitestarController(Controller):
    path = "/controller"

    @get(path="/resource/{redis_key:int}")
    @inject
    async def controller_endpoint(
        self,
        redis_key: int,
        redis: Annotated[Redis, _NoValidationDependency()] = Provide[Container.redis],
        num: Annotated[int, _NoValidationDependency()] = Provide[Container.num2],
    ) -> dict:
        value = redis.get(redis_key)
        return {"detail": value, "num2": num}


handlers = [
    litestar_endpoint,
    LitestarController,
    litestar_endpoint_object_provider,
]

app_deps = {}

app = Litestar(route_handlers=handlers, debug=True, dependencies=app_deps)


def test_litestar_endpoint_with_direct_provider_injection():
    with TestClient(app=app) as client:
        response = client.get("/some_resource")

    assert response.status_code == 200
    assert response.json() == {"detail": 800, "num2": 9402}


@pytest.mark.parametrize(
    "path_param",
    [
        -100,
        24234,
        -5,
    ],
)
def test_litestar_controller_endpoint(path_param: int):
    with TestClient(app=app) as client:
        response = client.get(f"/controller/resource/{path_param}")

    assert response.status_code == 200
    assert response.json() == {"detail": path_param, "num2": 9402}


def test_litestar_object_provider():
    with TestClient(app=app) as client:
        response = client.get("/num_endpoint")

    assert response.status_code == 200
    assert response.json() == {"detail": 9402}


def test_litestar_overriding_direct_provider_endpoint():
    mock_instance = Mock(get=lambda _: 192342526)
    override_providers = {"redis": mock_instance, "num2": -2999999999}

    with TestClient(app=app) as client:
        with Container.override_providers(override_providers):
            response = client.get("/some_resource")

    assert response.status_code == 200
    assert response.json() == {"detail": 192342526, "num2": -2999999999}


def test_litestar_endpoint_object_provider():
    with TestClient(app=app) as client:
        with Container.num2.override_context("mock_num2_value"):
            response = client.get("/num_endpoint")

    assert response.status_code == 200
    assert response.json() == {"detail": "mock_num2_value"}
