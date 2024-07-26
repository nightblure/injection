from typing import Callable as CallableType
from typing import TypeVar

from injection.providers.base_factory import BaseFactoryProvider

T = TypeVar("T")


class Callable(BaseFactoryProvider[T]):
    """Callable provider."""

    def __init__(self, callable_object: CallableType[..., T], *a, **kw):
        super().__init__(callable_object, *a, **kw)
