from typing import Any, TypeVar, Union, cast

from injection.providers.base import BaseProvider
from injection.resolving import resolve_value

T = TypeVar("T")


class Object(BaseProvider[T]):
    def __init__(self, obj: T) -> None:
        super().__init__()
        self._obj = obj

    def _resolve(self) -> T:
        value = cast(T, resolve_value(self._obj))
        return value

    def __call__(self) -> Union[T, Any]:
        if self._mocks:
            return self._mocks[-1]
        return self._resolve()
