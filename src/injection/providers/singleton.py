import sys
from typing import Any, Callable, Optional, TypeVar

if sys.version_info < (3, 10):
    from typing_extensions import ParamSpec
else:
    from typing import ParamSpec

from injection.providers.base_factory import BaseFactoryProvider

P = ParamSpec("P")
T = TypeVar("T")


class Singleton(BaseFactoryProvider[T]):
    """Object created only once"""

    def __init__(
        self,
        factory: Callable[P, T],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> None:
        super().__init__(factory, *args, **kwargs)
        self._instance: Optional[T] = None

    def _resolve(self, *args: Any, **kwargs: Any) -> T:
        if self._instance is None:
            instance = super()._resolve(*args, **kwargs)
            self._instance = instance

        return self._instance

    async def _async_resolve(self, *args: Any, **kwargs: Any) -> T:
        if self._instance is None:
            instance = await super()._async_resolve(*args, **kwargs)
            self._instance = instance

        return self._instance

    def reset(self) -> None:
        self._instance = None
