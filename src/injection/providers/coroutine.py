import sys
from typing import Any, Awaitable, Callable, NoReturn, TypeVar

if sys.version_info < (3, 10):
    from typing_extensions import ParamSpec
else:
    from typing import ParamSpec

from injection.providers.base_factory import BaseFactoryProvider

P = ParamSpec("P")
T = TypeVar("T")


class Coroutine(BaseFactoryProvider[T]):
    def __init__(
        self,
        factory: Callable[P, Awaitable[T]],
        *a: P.args,
        **kw: P.kwargs,
    ) -> None:
        super().__init__(factory, *a, **kw)

    def __call__(self, *_: Any, **__: Any) -> NoReturn:
        msg = "Coroutine provider cannot be resolved synchronously"
        raise RuntimeError(msg)
