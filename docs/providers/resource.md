# Resource

**Resource provider** provides a component with **initialization** and **closing**.
**Resource providers** supports next **initializers**:
* **sync** and **async** **generators**;
* **inheritors** of `ContextManager` and `AsyncContextManager` classes;
* functions wrapped into `@contextmanager` and `@asynccontextmanager` **decorators**.

## Resource scopes
Resource provider can works with two scopes: **singleton** and **function-scope**.

**Function-scope** requires to set parameter of `Resource` provider `function_scope=True`.
**Function-scope** resources can works only with `@inject` decorator!

## Example
```python
from typing import Tuple, Iterator, AsyncIterator

from injection import DeclarativeContainer, Provide, inject, providers


def sync_func() -> Iterator[str]:
    yield "sync_func"


async def async_func() -> AsyncIterator[str]:
    yield "async_func"


class DIContainer(DeclarativeContainer):
    sync_resource = providers.Resource(sync_func)
    async_resource = providers.Resource(async_func)

    sync_resource_func_scope = providers.Resource(sync_func, function_scope=True)
    async_resource_func_scope = providers.Resource(async_func, function_scope=True)


@inject
async def func_with_injections(
        sync_value: str = Provide[DIContainer.sync_resource],
        async_value: str = Provide[DIContainer.async_resource],
        sync_func_scope_value: str = Provide[DIContainer.sync_resource_func_scope],
        async_func_scope_value: str = Provide[DIContainer.async_resource_func_scope]
) -> Tuple[str, str, str, str]:
    return sync_value, async_value, sync_func_scope_value, async_func_scope_value


async def main() -> None:
    values = await func_with_injections()

    assert values == ("sync_func", "async_func", "sync_func", "async_func")

    assert DIContainer.sync_resource.initialized
    assert DIContainer.async_resource.initialized

    # Resources with function scope were closed after dependency injection
    assert not DIContainer.sync_resource_func_scope.initialized
    assert not DIContainer.async_resource_func_scope.initialized


if __name__ == "__main__":
    await main()
```

---

## Example with SQLAlchemy and FastAPI
```python
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
