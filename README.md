# Injection

![PyPI - Version](https://img.shields.io/pypi/v/deps-injection?label=pypi%20version)
![GitHub License](https://img.shields.io/github/license/nightblure/injection?color=012111012)

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/deps-injection)

[![Latest Release](https://github.com/nightblure/injection/actions/workflows/publish.yml/badge.svg)](https://github.com/nightblure/injection/actions/workflows/publish.yml)
[![Documentation Status](https://readthedocs.org/projects/injection/badge/?version=latest)](https://injection.readthedocs.io/en/latest/?badge=latest)

[![Tests And Linting](https://github.com/nightblure/injection/actions/workflows/ci.yml/badge.svg)](https://github.com/nightblure/injection/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/nightblure/injection/graph/badge.svg?token=2ZTFBlJqTb)](https://codecov.io/gh/nightblure/injection)

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)
[![pdm-managed](https://img.shields.io/endpoint?url=https%3A%2F%2Fcdn.jsdelivr.net%2Fgh%2Fpdm-project%2F.github%2Fbadge.json)](https://pdm-project.org)

[![Maintainability](https://api.codeclimate.com/v1/badges/1da49eb0b28eacae4624/maintainability)](https://codeclimate.com/github/nightblure/injection/maintainability)
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/nightblure/injection/total?color=102255102&label=Total%20downloads)

![PyPI - Month Downloads](https://img.shields.io/pypi/dm/deps-injection?color=102255102&label=Month%20downloads)
![GitHub Repo stars](https://img.shields.io/github/stars/nightblure/injection)

---

Easy dependency injection for all, works with Python 3.8-3.12. Main features and advantages:
* support **Python 3.8-3.12**;
* works with **FastAPI, Flask, Litestar** and **Django REST Framework**;
* dependency injection via `Annotated` in FastAPI;
* **no third-party dependencies**;
* **multiple containers**;
* **overriding** dependencies for tests without wiring;
* **100%** code coverage and very simple code;
* good [documentation](https://injection.readthedocs.io/latest/);
* intuitive and almost identical api with [dependency-injector](https://github.com/ets-labs/python-dependency-injector),
which will allow you to easily migrate to injection
(see [migration from dependency injector](https://injection.readthedocs.io/latest/dev/migration-from-dependency-injector.html));

---

## Installation
```shell
pip install deps-injection
```

## Using example

```python3
import sys

if sys.version_info >= (3, 9):
    from typing import Annotated
else:
    from typing import Annotated
from unittest.mock import Mock

import pytest
from fastapi import APIRouter, Depends, FastAPI
from fastapi.testclient import TestClient
from injection import DeclarativeContainer, Provide, inject, providers


class Settings:
    redis_url: str = "redis://localhost"
    redis_port: int = 6379


class Redis:
    def __init__(self, *, url: str, port: int):
        self.uri = url + ":" + str(port)
        self.url = url
        self.port = port

    def get(self, key):
        return key


class Container(DeclarativeContainer):
    settings = providers.Singleton(Settings)
    redis = providers.Singleton(
        Redis,
        port=settings.provided.redis_port,
        url=settings.provided.redis_url,
    )


router = APIRouter(prefix="/api")


def create_app():
    app = FastAPI()
    app.include_router(router)
    return app


RedisDependency = Annotated[Redis, Depends(Provide["redis"])]
RedisDependencyExplicit = Annotated[Redis, Depends(Provide[Container.redis])]


@router.get("/values")
@inject
def some_get_endpoint_handler(redis: RedisDependency):
    value = redis.get(299)
    return {"detail": value}


@router.post("/values")
@inject
async def some_get_async_endpoint_handler(redis: RedisDependencyExplicit):
    value = redis.get(399)
    return {"detail": value}


###################### TESTING ######################
@pytest.fixture(scope="session")
def app():
    return create_app()


@pytest.fixture(scope="session")
def container():
    return Container.instance()


@pytest.fixture()
def test_client(app):
    client = TestClient(app)
    return client


def test_override_providers(test_client, container):
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

```

---
