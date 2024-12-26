from contextlib import contextmanager
from typing import Callable, Iterator

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from injection import DeclarativeContainer, providers


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
