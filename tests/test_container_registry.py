from unittest import mock

import pytest
from injection.container_registry import ContainerRegistry


@mock.patch.object(ContainerRegistry, "_ContainerRegistry__get_containers")
def test_container_registry_fail_on_get_default_container(
    mock_get_containers_method,
    container_registry,
):
    match = "You should create at least one container"
    mock_get_containers_method.return_value = []

    with pytest.raises(Exception, match=match):
        container_registry.get_default_container()
