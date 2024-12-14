from random import Random
from typing import Any, AsyncIterator, Type
from unittest.mock import Mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from tests.container_objects import Container
from tests.integration.test_fastapi.app import create_app
from tests.integration.test_fastapi.sqlalchemy_resource_case import (
    SqlaResourceContainer,
)


@pytest.fixture(scope="session")
def app() -> FastAPI:
    return create_app()


@pytest.fixture(scope="session")
def test_client(app: FastAPI) -> TestClient:
    client = TestClient(app)
    return client


@pytest.fixture(scope="session")
async def async_client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app),
        base_url="http://testserver",
    ) as client:
        yield client


@pytest.mark.parametrize(
    "value",
    [1, 2, 5, 10, 245, -34636, 923425],
)
def test_sync_fastapi_endpoint(test_client: TestClient, value: int) -> None:
    response = test_client.get(f"/api/values/{value}")

    assert response.status_code == 200
    body = response.json()
    assert body["detail"] == value


def test_async_fastapi_endpoint(test_client: TestClient) -> None:
    response = test_client.post("/api/values")

    assert response.status_code == 200
    body = response.json()
    assert body["detail"] == 399


def test_async_fastapi_endpoint_expect_422_without_provide_marker(
    test_client: TestClient,
) -> None:
    response = test_client.post("/api/values-without_provide")

    assert response.status_code == 422
    body = response.json()
    assert body["detail"][0] == {
        "input": None,
        "loc": ["query", "args"],
        "msg": "Field required",
        "type": "missing",
    }
    assert body["detail"][1] == {
        "input": None,
        "loc": ["query", "kwargs"],
        "msg": "Field required",
        "type": "missing",
    }


@pytest.mark.parametrize(
    "override_value",
    ["mock_get_method_110934", "blsdfmsdfsf", -345627434],
)
def test_fastapi_override_provider(
    test_client: TestClient,
    container: Type[Container],
    override_value: Any,
) -> None:
    mock_redis = Mock()
    mock_redis.get = lambda _: override_value

    with container.override_providers_kwargs(redis=mock_redis):
        response = test_client.post("/api/values")

    assert response.status_code == 200
    body = response.json()
    assert body["detail"] == override_value


@pytest.fixture(scope="session")
def rnd() -> Random:
    return Random()  # noqa: S311


@pytest.fixture
def random_int(rnd: Random) -> int:
    return rnd.randint(1, 10**6)


def test_sqla_resource_sync_endpoint(test_client: TestClient, random_int: int) -> None:
    response = test_client.get(f"/sqlalchemy-resources/sync/{random_int}")

    assert response.status_code == 200
    assert not SqlaResourceContainer.db_session.initialized
    body = response.json()
    assert isinstance(body["detail"], int)


def test_sqla_resource_async_endpoint(test_client: TestClient, random_int: int) -> None:
    response = test_client.get(f"/sqlalchemy-resources/async/{random_int}")

    assert response.status_code == 200
    assert not SqlaResourceContainer.db_session.initialized
    body = response.json()
    assert isinstance(body["detail"], int)
