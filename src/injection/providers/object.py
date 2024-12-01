from typing import TypeVar, cast

from injection.providers.base import BaseProvider

T = TypeVar("T")


class Object(BaseProvider[T]):
    def __init__(self, obj: T) -> None:
        super().__init__()
        self._obj = obj

    def _resolve(self) -> T:
        return self._obj

    def __call__(self) -> T:
        if self._mocks:
            return cast(T, self._mocks[-1])
        return self._resolve()
