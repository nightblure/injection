# Flask

## Example with SQLAlchemy and pytest
```python
from contextlib import contextmanager
from random import Random
from typing import Any, Callable, Dict, Iterator
from unittest.mock import Mock

import pytest
from flask import Flask, request
from flask.testing import FlaskClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from injection import DeclarativeContainer, Provide, auto_inject, inject, providers


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


class SqlaResourceContainer(DeclarativeContainer):
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


@pytest.fixture
def sqla_container() -> SqlaResourceContainer:
    return SqlaResourceContainer()


app = Flask(__name__)
# https://flask.palletsprojects.com/en/stable/testing/
app.config.update({"TESTING": True})


@app.route("/some_resource/<int:value>", methods=["GET"])
@inject
def flask_endpoint(
    value: int,
    some_dao: SomeDAO = Provide[SqlaResourceContainer.some_dao],
) -> Dict[str, Any]:
    value = some_dao.get_some_data(num=value)
    return {"detail": value}


@app.route("/auto-inject-endpoint", methods=["POST"])
@auto_inject(target_container=SqlaResourceContainer)
def flask_endpoint_auto_inject(some_dao: SomeDAO) -> Dict[str, Any]:
    body: Dict[str, Any] = request.get_json()
    value = some_dao.get_some_data(num=body["num"])
    return {"detail": value}


##################################################### TESTS ############################################################
@pytest.fixture
def random_int() -> int:
    rnd = Random()  # noqa: S311
    return rnd.randint(1, 10**6)


@pytest.fixture(scope="session")
def test_client() -> FlaskClient:
    return app.test_client()


def test_flask_endpoint(
    test_client: FlaskClient,
    random_int: int,
    sqla_container: SqlaResourceContainer,
) -> None:
    response = test_client.get(f"/some_resource/{random_int}")

    assert response.status_code == 200
    assert response.json == {"detail": random_int}
    assert not sqla_container.db_session.initialized


def test_flask_endpoint_auto_inject(
    test_client: FlaskClient,
    random_int: int,
    sqla_container: SqlaResourceContainer,
) -> None:
    response = test_client.post("/auto-inject-endpoint", json={"num": random_int})

    assert response.status_code == 200
    assert response.json == {"detail": random_int}
    assert not sqla_container.db_session.initialized


@pytest.mark.parametrize(
    "override_value",
    ["mock_get_method_110934", "blsdfmsdfsf", -345627434],
)
def test_flask_override_provider(
    test_client: FlaskClient,
    sqla_container: SqlaResourceContainer,
    override_value: Any,
) -> None:
    mock_dao = Mock()
    mock_dao.get_some_data = lambda num: num

    with sqla_container.override_providers_kwargs(some_dao=mock_dao):
        response = test_client.post(
            "auto-inject-endpoint",
            json={"num": override_value},
        )

    assert response.status_code == 200
    assert response.json == {"detail": override_value}
```
