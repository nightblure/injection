from functools import partial
from typing import Callable as CallableType
from typing import TypeVar

from injection.providers.base_factory import BaseFactoryProvider

T = TypeVar("T")
F = CallableType[..., T]


class PartialCallable(BaseFactoryProvider[F]):
    def __init__(self, callable_object: F, *a, **kw):
        super().__init__(callable_object, *a, **kw)

    def _resolve(self, *args, **kwargs) -> F:
        final_args, final_kwargs = self._get_final_args_and_kwargs(*args, **kwargs)
        partial_callable = partial(self._factory, *final_args, **final_kwargs)
        return partial_callable
