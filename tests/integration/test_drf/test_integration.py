import os
from typing import Any, Type
from unittest.mock import Mock

import django
import pytest

from tests.container_objects import Container

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "tests.integration.test_drf.drf_test_project.settings",
)
django.setup()
from rest_framework.test import APIClient  # noqa: E402


@pytest.fixture
def test_drf_client() -> APIClient:
    return APIClient()


def test_drf_get_endpoint(test_drf_client: APIClient) -> None:
    response = test_drf_client.get("http://127.0.0.1:8000/some_view_prefix")
    response_body = response.json()

    assert response.status_code == 200
    assert response_body == {"redis_url": "redis://localhost"}


def test_drf_post_endpoint(test_drf_client: APIClient) -> None:
    redis_key = 234214

    response = test_drf_client.post(
        "http://127.0.0.1:8000/some_view_prefix",
        data={"key": redis_key},
    )

    assert response.status_code == 201
    response_body = response.json()
    assert response_body == {"redis_key": redis_key}


@pytest.mark.parametrize(
    "override_value",
    ["kjgfiyrdi", "o987ytvydut", "-gfd56a`^^~Wyerjg"],
)
def test_drf_override_provider(
    test_drf_client: APIClient,
    container: Type[Container],
    override_value: Any,
) -> None:
    mock_redis = Mock(url=override_value)

    with container.override_providers_kwargs(redis=mock_redis):
        response = test_drf_client.get("http://127.0.0.1:8000/some_view_prefix")

    assert response.status_code == 200
    response_body = response.json()
    assert response_body == {"redis_url": override_value}
