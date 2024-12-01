from typing import TypeVar, cast

from injection.providers.base import BaseProvider

T = TypeVar("T")


class ClassGetItemMeta(type):
    def __getitem__(cls, item: BaseProvider[T]) -> T:
        return cast(T, cls(item))


class Provide(metaclass=ClassGetItemMeta):
    def __init__(self, provider: BaseProvider[T]) -> None:
        self.provider = provider

    def __call__(self) -> "Provide":
        return self
