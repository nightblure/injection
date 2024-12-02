from typing import AsyncIterator, Type

import pytest

from tests.container_objects import Container


@pytest.fixture(scope="session")
def container() -> Type[Container]:
    return Container


@pytest.fixture(autouse=True)
async def _close_resources(container: Type[Container]) -> AsyncIterator[None]:
    yield
    container.close_resources()
    await container.close_resources_async()
