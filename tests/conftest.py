import pytest
from injection.container_registry import ContainerRegistry

from tests.container_objects import Container


@pytest.fixture(scope="session")
def container_registry():
    return ContainerRegistry


@pytest.fixture(scope="session")
def container():
    return Container


# need this because container registry is singleton
# @pytest.fixture(autouse=True)
# def _force_clean_container_registry(container):
#     container.reset_override()
