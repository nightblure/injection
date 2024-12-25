from typing import AsyncIterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from tests.integration.test_fastapi.app import create_app


@pytest.fixture(scope="session")
def app() -> FastAPI:
    return create_app()


@pytest.fixture(scope="session")
def test_client(app: FastAPI) -> TestClient:
    client = TestClient(app)
    return client


@pytest.fixture(scope="session")
async def async_client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app),
        base_url="http://testserver",
    ) as client:
        yield client
