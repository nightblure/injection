from typing import Callable, TypeVar

from injection.providers.base import BaseProvider
from injection.resolving import get_clean_args, get_clean_kwargs

T = TypeVar("T")


class Coroutine(BaseProvider[T]):
    def __init__(self, coroutine: Callable, *a, **kw):
        super().__init__()
        self.coroutine = coroutine
        self.args = a
        self.kwargs = kw
        self._instance = None

    async def _resolve(self, *args, **kwargs):
        clean_args = get_clean_args(self.args)
        clean_kwargs = get_clean_kwargs(self.kwargs)

        final_args = []
        final_args.extend(clean_args)
        final_args.extend(args)

        final_kwargs = {}
        final_kwargs.update(clean_kwargs)
        final_kwargs.update(kwargs)

        result = await self.coroutine(*final_args, **final_kwargs)
        return result
