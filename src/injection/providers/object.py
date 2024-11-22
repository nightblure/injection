from typing import Any, TypeVar, Union

from injection.providers.base import BaseProvider

T = TypeVar("T")


class Object(BaseProvider[T]):
    def __init__(self, obj: T) -> None:
        super().__init__()
        self._obj = obj

    def _resolve(self) -> T:
        return self._obj

    def __call__(self) -> Union[T, Any]:
        if self._mocks:
            return self._mocks[-1]
        return self._resolve()
