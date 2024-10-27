from functools import partial
from typing import Any, Callable, TypeVar, cast

from typing_extensions import ParamSpec

from injection.providers.base_factory import BaseFactoryProvider

P = ParamSpec("P")
T = TypeVar("T")


class PartialCallable(BaseFactoryProvider[T]):
    def __init__(
        self,
        callable_object: Callable[P, T],
        *a: P.args,
        **kw: P.kwargs,
    ) -> None:
        super().__init__(callable_object, *a, **kw)

    def _resolve(self, *args: Any, **kwargs: Any) -> Callable[P, T]:
        final_args, final_kwargs = self._get_final_args_and_kwargs(*args, **kwargs)
        partial_callable = cast(
            Callable[P, T],
            partial(self._factory, *final_args, **final_kwargs),
        )
        return partial_callable
