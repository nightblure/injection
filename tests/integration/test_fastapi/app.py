from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from tests.integration.test_fastapi.handlers import router


@asynccontextmanager
async def lifespan_handler(_: FastAPI) -> AsyncIterator[None]:
    yield


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan_handler)
    app.include_router(router)
    return app
