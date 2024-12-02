from typing import TypeVar

from injection.providers.base import BaseProvider

T = TypeVar("T")


class Object(BaseProvider[T]):
    def __init__(self, value: T) -> None:
        super().__init__()
        self._value = value

    def _resolve(self) -> T:
        return self._value

    async def _async_resolve(self) -> T:
        return self._value
