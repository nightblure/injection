from typing import Awaitable, Callable, TypeVar

from typing_extensions import ParamSpec

from injection.providers.base_factory import BaseFactoryProvider

P = ParamSpec("P")
T = TypeVar("T")


class Coroutine(BaseFactoryProvider[T]):
    def __init__(
        self,
        coroutine: Callable[P, Awaitable[T]],
        *a: P.args,
        **kw: P.kwargs,
    ) -> None:
        super().__init__(coroutine, *a, **kw)
