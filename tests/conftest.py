from typing import Type

import pytest

from tests.container_objects import Container


@pytest.fixture(scope="session")
def container() -> Type[Container]:
    return Container
