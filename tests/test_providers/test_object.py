from dataclasses import dataclass
from typing import Any, Type
from unittest.mock import Mock

import pytest

from injection import Provide, inject, providers
from tests.container_objects import Container


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


def test_object_provider_overriding_with_sync_injection(
    container: Type[Container],
) -> None:
    @inject
    def _inner(
        v: Any = Provide[container.num],
    ) -> str:
        return v()  # type: ignore[no-any-return]

    with container.num.override_context(Mock(return_value="mock")):
        value = _inner()

    assert value == "mock"


async def test_object_provider_overriding_with_async_injection(
    container: Type[Container],
) -> None:
    @inject
    async def _inner(
        v: Any = Provide[container.num],
    ) -> str:
        return v()  # type: ignore[no-any-return]

    with container.num.override_context(Mock(return_value="mock")):
        value = await _inner()

    assert value == "mock"
