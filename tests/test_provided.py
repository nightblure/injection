from typing import Type

import pytest

from injection.provided import ProvidedInstance
from tests.container_objects import Container


def test_provider_resolving_fail_on_provided_without_any_attributes(
    container: Type[Container],
) -> None:
    provided = ProvidedInstance(container.settings)
    assert len(provided._attrs) == 0

    with pytest.raises(Exception) as e:
        provided.get_value()

    assert (
        e.value.args[0]
        == "Please provide at least one attribute. For example: provide.some_attr"
    )

def test_provided_instance_attribute_call(container: Type[Container]) -> None:
    provided = ProvidedInstance(container.some_service)

    provided_property = provided.do_smth

    assert provided_property.call() == 'Doing smth 2'
    assert provided_property.get_value()() == 'Doing smth 2'