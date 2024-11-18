from typing import Any, Union
from unittest.mock import Mock

from litestar import Litestar, get
from litestar.testing import TestClient

from injection import Provide, inject
from tests.container_objects import Container, Redis


@get(
    "/some_resource",
    status_code=200,
)
@inject
async def litestar_endpoint(
    redis: Union[Redis, Any] = Provide[Container.redis],
    num: Union[int, Any] = Provide[Container.num2],
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


_handlers = [
    litestar_endpoint,
    litestar_endpoint_object_provider,
]

app_deps = {}

app = Litestar(route_handlers=_handlers, debug=True, dependencies=app_deps)


def test_litestar_endpoint_with_direct_provider_injection():
    with TestClient(app=app) as client:
        response = client.get("/some_resource")

    assert response.status_code == 200
    assert response.json() == {"detail": 800, "num2": 9402}


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
