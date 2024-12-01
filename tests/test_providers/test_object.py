from dataclasses import dataclass
from typing import Any

import pytest

from injection import providers


@dataclass
class SomeClass: ...


@pytest.mark.parametrize(
    ("obj", "expected"),
    [
        (SomeClass, type(SomeClass)),
        (SomeClass(), SomeClass),
        ("some_class", str),
        (234525, int),
    ],
)
def test_object_provider_resolve_with_expected_type(obj: Any, expected: Any) -> None:
    provider = providers.Object(obj)

    assert isinstance(provider(), expected)


@pytest.mark.parametrize(
    ("obj", "expected"),
    [
        (type, type),
        (234525, 234525),
        (object, object),
        ("some_class", "some_class"),
    ],
)
def test_object_provider_resolve_with_expected_value(obj: Any, expected: Any) -> None:
    provider = providers.Object(obj)

    assert provider() == expected
