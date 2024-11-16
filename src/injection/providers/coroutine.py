from typing import Any, Awaitable, Callable, TypeVar, cast

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
        super().__init__(cast(Callable[P, T], coroutine), *a, **kw)

    def __call__(self, *args: Any, **kwargs: Any) -> Awaitable[T]:
        return cast(Awaitable[T], super().__call__(*args, **kwargs))
