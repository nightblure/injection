from typing import Any
from unittest.mock import Mock

import pytest
from flask import Flask

from injection import Provide, auto_inject, inject
from tests.container_objects import Container, Redis

app = Flask(__name__)
app.config.update({"TESTING": True})


@app.route("/some_resource")
@inject
def flask_endpoint(redis: Redis = Provide[Container.redis]):
    value = redis.get(-900)
    return {"detail": value}


@app.route("/auto-inject-endpoint", methods=["POST"])
@auto_inject
def flask_endpoint_auto_inject(redis: Redis):
    value = redis.get(-900)
    return {"detail": value}


@pytest.fixture
def test_client():
    return app.test_client()


def test_flask_endpoint(test_client):
    response = test_client.get("/some_resource")

    assert response.status_code == 200
    assert response.json == {"detail": -900}


def test_flask_endpoint_auto_inject(test_client):
    response = test_client.post("/auto-inject-endpoint")

    assert response.status_code == 200
    assert response.json == {"detail": -900}


@pytest.mark.parametrize(
    "override_value",
    ["mock_get_method_110934", "blsdfmsdfsf", -345627434],
)
def test_flask_override_provider(test_client, container, override_value: Any):
    mock_redis = Mock()
    mock_redis.get = lambda _: override_value

    with container.override_providers_kwargs(redis=mock_redis):
        response = test_client.post("auto-inject-endpoint")

    assert response.status_code == 200
    assert response.json == {"detail": override_value}
