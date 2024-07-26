from typing import Union

from injection.providers.base import BaseProvider


class ClassGetItemMeta(type):
    def __getitem__(cls, item: Union[str, BaseProvider]) -> "Provide":
        return cls(item)


class Provide(metaclass=ClassGetItemMeta):
    def __init__(self, provider: Union[str, BaseProvider]) -> None:
        self.provider = provider

    def __call__(self) -> "Provide":
        return self
