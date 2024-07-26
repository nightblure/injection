from dataclasses import dataclass

import pytest
from injection import providers


@dataclass
class SomeClass:
    field1: str
    field2: int


@pytest.fixture()
def transient_provider():
    return providers.Transient(SomeClass, field1="value", field2=1)


def test_transient_provider_override_args(transient_provider):
    resolved = transient_provider(field1="new_value", field2=100)
    assert resolved.field1 == "new_value"
    assert resolved.field2 == 100

    resolved = transient_provider()
    assert resolved.field1 == "value"
    assert resolved.field2 == 1


def test_reset_override_not_fail_when_no_mocks(transient_provider):
    transient_provider.reset_override()
    transient_provider.reset_override()
