import sys
from contextlib import contextmanager
from typing import Any, Callable, Dict, Iterator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

if sys.version_info >= (3, 9):
    from typing import Annotated
else:
    from typing_extensions import Annotated

from fastapi import APIRouter, Depends

from injection import DeclarativeContainer, Provide, inject, providers

router = APIRouter(prefix="/sqlalchemy-resources")


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


SomeDAODependency = Annotated[SomeDAO, Depends(Provide[SqlaResourceContainer.some_dao])]


@router.get("/sync/{value}")
@inject
def sqla_resource_handler_sync(
    some_dao: SomeDAODependency,
    value: int,
) -> Dict[str, Any]:
    value = some_dao.get_some_data(num=value)
    return {"detail": value}


@router.get("/async/{value}")
@inject
async def sqla_resource_handler_async(
    some_dao: SomeDAODependency,
    value: int,
) -> Dict[str, Any]:
    value = some_dao.get_some_data(num=value)
    return {"detail": value}
