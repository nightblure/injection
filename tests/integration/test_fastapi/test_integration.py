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


def test_sync_fastapi_endpoint(test_client):
    response = test_client.get("/api/values")

    assert response.status_code == 200
    body = response.json()
    assert body["detail"] == 299


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


def test_fastapi_override_provider(test_client, container):
    def mock_get_method(_):
        return "mock_get_method"

    mock_redis = Mock()
    mock_redis.get = mock_get_method

    providers_to_override = {"redis": mock_redis}

    with container.override_providers(providers_to_override):
        response = test_client.get("/api/values")

    assert response.status_code == 200
    body = response.json()
    assert body["detail"] == "mock_get_method"
