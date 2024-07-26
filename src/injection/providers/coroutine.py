from typing import Callable, TypeVar

from injection.providers.base_factory import BaseFactoryProvider

T = TypeVar("T")


class Coroutine(BaseFactoryProvider[T]):
    def __init__(self, coroutine: Callable, *a, **kw):
        super().__init__(coroutine, *a, **kw)
