import pytest
from injection import Provide
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

    error_msg = f"Incorrect marker type: {type(object)!r}. Marker parameter must be either BaseProvider."
    assert e.value.args[0] == error_msg
