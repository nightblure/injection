from operator import attrgetter
from typing import TYPE_CHECKING, Any, List

if TYPE_CHECKING:
    from injection.providers.base import BaseProvider


def _get_value_from_object_by_dotted_path(obj: Any, path: str) -> Any:
    # https://stackoverflow.com/questions/31174295/getattr-and-setattr-on-nested-subobjects-chained-properties
    attribute_getter = attrgetter(path)
    attr_value = attribute_getter(obj)
    return attr_value


class ProvidedInstance:
    def __init__(self, provided: "BaseProvider[Any]"):
        self._provided = provided
        self._attrs: List[str] = []

    def __getattr__(self, attr: str) -> "ProvidedInstance":
        self._attrs.append(attr)
        return self

    def get_value(self) -> Any:
        resolved_provider_object = self._provided()

        if not self._attrs:
            msg = "Please provide at least one attribute. For example: ...provide.some_attr..."
            raise Exception(msg)

        attribute_path = ".".join(self._attrs)
        attr_value = _get_value_from_object_by_dotted_path(
            resolved_provider_object,
            attribute_path,
        )
        return attr_value
