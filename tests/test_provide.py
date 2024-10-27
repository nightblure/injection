import pytest

from injection import Provide


@pytest.mark.parametrize("value", [(1,), (object,)])
def test_provide_returns_self(value):
    provide = Provide[value]
    assert provide is provide()
    assert provide.provider is value
