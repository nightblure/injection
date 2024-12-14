from typing import Any, Dict, Type
from unittest.mock import Mock

import pytest
from flask import Flask
from flask.testing import FlaskClient

from injection import Provide, auto_inject, inject
from tests.container_objects import Container, Redis

app = Flask(__name__)
app.config.update({"TESTING": True})


@app.route("/some_resource", methods=["GET"])
@inject
def flask_endpoint(redis: Redis = Provide[Container.redis]) -> Dict[str, Any]:
    value = redis.get(-900)
    return {"detail": value}


@app.route("/auto-inject-endpoint", methods=["POST"])
@auto_inject(target_container=Container)
def flask_endpoint_auto_inject(redis: Redis) -> Dict[str, Any]:
    value = redis.get(-900)
    return {"detail": value}


@pytest.fixture
def test_client() -> FlaskClient:
    return app.test_client()


def test_flask_endpoint(test_client: FlaskClient) -> None:
    response = test_client.get("/some_resource")

    assert response.status_code == 200
    assert response.json == {"detail": -900}


def test_flask_endpoint_auto_inject(test_client: FlaskClient) -> None:
    response = test_client.post("/auto-inject-endpoint")

    assert response.status_code == 200
    assert response.json == {"detail": -900}


@pytest.mark.parametrize(
    "override_value",
    ["mock_get_method_110934", "blsdfmsdfsf", -345627434],
)
def test_flask_override_provider(
    test_client: FlaskClient,
    container: Type[Container],
    override_value: Any,
) -> None:
    mock_redis = Mock()
    mock_redis.get = lambda _: override_value

    with container.override_providers_kwargs(redis=mock_redis):
        response = test_client.post("auto-inject-endpoint")

    assert response.status_code == 200
    assert response.json == {"detail": override_value}
