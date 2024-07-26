from typing import Type, TypeVar

from injection.providers.base_factory import BaseFactoryProvider

T = TypeVar("T")


class Transient(BaseFactoryProvider[T]):
    """Object that needs to be created every time"""

    def __init__(self, type_cls: Type[T], *a, **kw):
        super().__init__(type_cls, *a, **kw)
        self.type_cls = type_cls
