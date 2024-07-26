from dataclasses import dataclass

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
def test_object_provider_resolving(obj, expected):
    provider = providers.Object(obj)
    assert isinstance(provider(), expected)
