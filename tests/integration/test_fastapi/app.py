from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from tests.integration.test_fastapi.handlers import router
from tests.integration.test_fastapi.sqlalchemy_resource_case import (
    router as sqla_router,
)

routers = [
    router,
    sqla_router,
]


@asynccontextmanager
async def lifespan_handler(_: FastAPI) -> AsyncIterator[None]:
    yield


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan_handler)

    for router_ in routers:
        app.include_router(router_)

    return app
