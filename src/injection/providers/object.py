from typing import TypeVar

from injection.providers.base import BaseProvider
from injection.resolving import resolve_value

T = TypeVar("T")


class Object(BaseProvider[T]):
    def __init__(self, obj: T) -> None:
        super().__init__()
        self._obj = obj

    def _resolve(self) -> T:
        value = resolve_value(self._obj)
        return value
