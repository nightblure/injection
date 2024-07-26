from contextlib import asynccontextmanager

from fastapi import FastAPI

from tests.test_integrations.test_fastapi.handlers import router


@asynccontextmanager
async def lifespan_handler(_):
    yield


def create_app():
    app = FastAPI(lifespan=lifespan_handler)
    app.include_router(router)
    return app
