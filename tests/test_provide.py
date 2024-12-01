from typing import Any

import pytest

from injection import Provide


@pytest.mark.parametrize("value", [(1,), (object,)])
def test_provide_returns_self(value: Any) -> None:
    provide = Provide[value]  # type: ignore[type-arg]

    assert isinstance(provide, Provide)
    assert provide.provider is value
