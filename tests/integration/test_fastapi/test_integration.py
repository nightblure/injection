from typing import Any
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from tests.integration.test_fastapi.app import create_app


@pytest.fixture(scope="session")
def app():
    return create_app()


@pytest.fixture
def test_client(app):
    client = TestClient(app)
    return client


@pytest.mark.parametrize(
    "value",
    [1, 2, 5, 10, 245, -34636, 923425],
)
def test_sync_fastapi_endpoint(test_client, value: int):
    response = test_client.get(f"/api/values/{value}")

    assert response.status_code == 200
    body = response.json()
    assert body["detail"] == value


def test_async_fastapi_endpoint(test_client):
    response = test_client.post("/api/values")

    assert response.status_code == 200
    body = response.json()
    assert body["detail"] == 399


def test_async_fastapi_endpoint_expect_422_without_provide_marker(test_client):
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
def test_fastapi_override_provider(test_client, container, override_value: Any):
    mock_redis = Mock()
    mock_redis.get = lambda _: override_value

    with container.override_providers_kwargs(redis=mock_redis):
        response = test_client.post("/api/values")

    assert response.status_code == 200
    body = response.json()
    assert body["detail"] == override_value
