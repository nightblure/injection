from typing import Callable as CallableType
from typing import TypeVar

from typing_extensions import ParamSpec

from injection.providers.base_factory import BaseFactoryProvider

P = ParamSpec("P")
T = TypeVar("T")


class Callable(BaseFactoryProvider[T]):
    """Callable provider."""

    def __init__(
        self,
        callable_object: CallableType[P, T],
        *a: P.args,
        **kw: P.kwargs,
    ) -> None:
        super().__init__(callable_object, *a, **kw)
