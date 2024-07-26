from typing import Any, Callable, TypeVar

from injection.providers.base import BaseProvider
from injection.resolving import get_clean_args, get_clean_kwargs

T = TypeVar("T")


class Callable(BaseProvider[T]):
    """Callable provider."""

    def __init__(self, callable_object: Callable, *a, **kw):
        super().__init__()
        self.callable_object = callable_object
        self.args = a
        self.kwargs = kw
        self._instance = None

    def _resolve(self, *args, **kwargs) -> Any:
        clean_args = get_clean_args(self.args)
        clean_kwargs = get_clean_kwargs(self.kwargs)

        final_args = []
        final_args.extend(clean_args)
        final_args.extend(args)

        final_kwargs = {}
        final_kwargs.update(clean_kwargs)
        final_kwargs.update(kwargs)

        result = self.callable_object(*final_args, **final_kwargs)
        return result
