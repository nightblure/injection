import pytest

from injection.provided import ProvidedInstance


def test_provider_resolving_fail_on_provided_without_any_attributes(container):
    provided = ProvidedInstance(container.settings)
    assert len(provided._attrs) == 0

    with pytest.raises(Exception) as e:
        provided.get_value()

    assert (
        e.value.args[0]
        == "Please provide at least one attribute. For example: ...provide.some_attr..."
    )
