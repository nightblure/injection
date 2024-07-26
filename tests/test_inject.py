from unittest.mock import patch

import pytest
from injection import Provide
from injection.container_registry import ContainerRegistry
from injection.inject import _resolve_provide_marker


def test_resolve_provide_marker_fail_when_marker_is_not_provide_type(container):
    with pytest.raises(Exception) as e:
        _resolve_provide_marker(container.redis)

    assert (
        e.value.args[0]
        == f"Incorrect marker type: {type(container.redis)!r}. Marker must be either Provide."
    )


def test_resolve_provide_marker_fail_when_marker_parameter_has_incorrect_type():
    with pytest.raises(Exception) as e:
        _resolve_provide_marker(Provide[object])

    error_msg = f"Incorrect marker type: {type(object)!r}. Marker parameter must be either str or BaseProvider."
    assert e.value.args[0] == error_msg


@patch.object(ContainerRegistry, "get_containers_count")
def test_container_registry_fail_with_string_marker_when_containers_more_than_one(
    mock_get_containers_count_method,
):
    error_msg = "Please specify the container and its provider explicitly"
    mock_get_containers_count_method.return_value = 2

    with pytest.raises(Exception) as e:
        _resolve_provide_marker(Provide["redis"])

    assert e.value.args[0] == error_msg
