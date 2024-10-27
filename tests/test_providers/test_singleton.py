from dataclasses import dataclass

import pytest

from injection import providers


@dataclass
class SomeClass:
    field1: str
    field2: int


def test_singleton_override_args():
    singleton_provider = providers.Singleton(SomeClass, field1="value", field2=1)

    resolved = singleton_provider(field1="new_value", field2=100)
    assert resolved.field1 == "new_value"
    assert resolved.field2 == 100

    singleton_provider.reset()
    resolved = singleton_provider()
    assert resolved.field1 == "value"
    assert resolved.field2 == 1


def test_singleton_resolving_with_override_params_no_work_without_reset_cache():
    singleton_provider = providers.Singleton(SomeClass, field1="value", field2=1)

    resolved = singleton_provider(field1="new_value", field2=100)
    assert resolved.field1 == "new_value"
    assert resolved.field2 == 100

    resolved = singleton_provider(field1="override_value", field2=239)

    with pytest.raises(AssertionError):
        assert resolved.field1 == "override_value"

    with pytest.raises(AssertionError):
        assert resolved.field2 == 239


def test_singleton_reset_smoke():
    provider = providers.Singleton(SomeClass, field1="...", field2=-9000)
    obj = provider()
    obj2 = provider()

    assert obj is obj2
    provider.reset()

    obj3 = provider()
    assert obj is not obj3
    assert obj2 is not obj3
