# Injection

![PyPI - Version](https://img.shields.io/pypi/v/deps-injection?label=pypi%20version&color=012111012)
![GitHub License](https://img.shields.io/github/license/nightblure/injection?color=012111012)

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/deps-injection)

[![Latest Release](https://github.com/nightblure/injection/actions/workflows/publish.yml/badge.svg)](https://github.com/nightblure/injection/actions/workflows/publish.yml)
[![Documentation Status](https://readthedocs.org/projects/injection/badge/?version=latest)](https://injection.readthedocs.io/en/latest/?badge=latest)

[![Tests And Linting](https://github.com/nightblure/injection/actions/workflows/ci.yml/badge.svg)](https://github.com/nightblure/injection/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/nightblure/injection/graph/badge.svg?token=2ZTFBlJqTb)](https://codecov.io/gh/nightblure/injection)

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![MyPy Strict](https://img.shields.io/badge/mypy-strict-blue)](https://mypy.readthedocs.io/en/stable/getting_started.html#strict-mode-and-configuration)

[![Maintainability](https://api.codeclimate.com/v1/badges/1da49eb0b28eacae4624/maintainability)](https://codeclimate.com/github/nightblure/injection/maintainability)
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/nightblure/injection/total?color=102255102&label=Total%20downloads)

![PyPI - Month Downloads](https://img.shields.io/pypi/dm/deps-injection?color=102255102&label=Month%20downloads)
![GitHub Repo stars](https://img.shields.io/github/stars/nightblure/injection)

---

Easy dependency injection for all, works with Python 3.8-3.13. Main features and advantages:
* support **Python 3.8-3.13**;
* works with **FastAPI, **Litestar**, Flask** and **Django REST Framework**;
* support **dependency** **injection** via `Annotated` in `FastAPI`;
* support **async injections**;
* support [**auto injection by types**](https://injection.readthedocs.io/latest/injection/auto_injection.html); 
* [**resources**](https://injection.readthedocs.io/latest/providers/resource.html) with **function scope**;
* no **wiring**;
* **overriding** dependencies for testing;
* **100%** code coverage;
* the code is fully **typed** and checked with [mypy](https://github.com/python/mypy);
* good [documentation](https://injection.readthedocs.io/latest/);
* intuitive and almost identical api with [dependency-injector](https://github.com/ets-labs/python-dependency-injector),
which will allow you to easily migrate to injection
(see [migration from dependency injector](https://injection.readthedocs.io/latest/dev/migration-from-dependency-injector.html));

---

## Installation
```shell
pip install deps-injection
```

## Compatibility between web frameworks and injection features
| Framework                                                                | Dependency injection with @inject | Overriding providers |    Dependency injection with @autoinject    |
|--------------------------------------------------------------------------|:---------------------------------:|:--------------------:|:-------------------------------------------:|
| [FastAPI](https://github.com/fastapi/fastapi)                            |                 ✅                 |          ✅           |                      ➖                      |
| [Flask](https://github.com/pallets/flask)                                |                 ✅                 |          ✅           |                      ✅                      |
| [Django REST Framework](https://github.com/encode/django-rest-framework) |                 ✅                 |          ✅           |                      ✅                      |
| [Litestar](https://github.com/litestar-org/litestar)                     |                 ✅                 |          ✅           |                      ➖                      |                           ➖                            |


## Quickstart with FastAPI, SQLAlchemy and pytest
```python3
from contextlib import contextmanager
from random import Random
from typing import Annotated, Any, Callable, Dict, Iterator

import pytest
from fastapi import Depends, FastAPI
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from starlette.testclient import TestClient

from injection import DeclarativeContainer, Provide, inject, providers


@contextmanager
def db_session_resource(session_factory: Callable[..., Session]) -> Iterator[Session]:
    session = session_factory()
    try:
        yield session
    except Exception:
        session.rollback()
    finally:
        session.close()


class SomeDAO:
    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session

    def get_some_data(self, num: int) -> int:
        stmt = text("SELECT :num").bindparams(num=num)
        data: int = self.db_session.execute(stmt).scalar_one()
        return data


class DIContainer(DeclarativeContainer):
    db_engine = providers.Singleton(
        create_engine,
        url="sqlite:///db.db",
        pool_size=20,
        max_overflow=0,
        pool_pre_ping=False,
    )

    session_factory = providers.Singleton(
        sessionmaker,
        db_engine.cast,
        autoflush=False,
        autocommit=False,
    )

    db_session = providers.Resource(
        db_session_resource,
        session_factory=session_factory.cast,
        function_scope=True,
    )

    some_dao = providers.Factory(SomeDAO, db_session=db_session.cast)


SomeDAODependency = Annotated[SomeDAO, Depends(Provide[DIContainer.some_dao])]

app = FastAPI()


@app.get("/values/{value}")
@inject
async def sqla_resource_handler_async(
    value: int,
    some_dao: SomeDAODependency,
) -> Dict[str, Any]:
    value = some_dao.get_some_data(num=value)
    return {"detail": value}


@pytest.fixture(scope="session")
def test_client() -> TestClient:
    client = TestClient(app)
    return client


def test_sqla_resource(test_client: TestClient) -> None:
    rnd = Random()
    random_int = rnd.randint(-(10**6), 10**6)

    response = test_client.get(f"/values/{random_int}")

    assert response.status_code == 200
    assert not DIContainer.db_session.initialized
    body = response.json()
    assert body["detail"] == random_int
    
```
