import sys
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Any, Generic, Iterator, List, TypeVar, cast

if sys.version_info < (3, 10):
    from typing_extensions import ParamSpec
else:
    from typing import ParamSpec

from injection.provided import ProvidedInstance

P = ParamSpec("P")
T = TypeVar("T")


class BaseProvider(Generic[T], ABC):
    def __init__(self) -> None:
        self._mocks: List[Any] = []

    @abstractmethod
    def _resolve(self, *args: Any, **kwargs: Any) -> T:
        raise NotImplementedError

    async def _async_resolve(self, *args: Any, **kwargs: Any) -> T:
        return self._resolve(*args, **kwargs)

    async def async_resolve(self, *args: Any, **kwargs: Any) -> T:
        if self._mocks:
            return cast(T, self._mocks[-1])
        return await self._async_resolve(*args, **kwargs)

    def __call__(self, *args: Any, **kwargs: Any) -> T:
        if self._mocks:
            return cast(T, self._mocks[-1])
        return self._resolve(*args, **kwargs)

    @property
    def provided(self) -> ProvidedInstance:
        return ProvidedInstance(provided=self)

    def override(self, mock: Any) -> None:
        self._mocks.append(mock)

    @contextmanager
    def override_context(self, mock: Any) -> Iterator[None]:
        self.override(mock)
        try:
            yield
        finally:
            self.reset_override()

    def reset_override(self) -> None:
        if not self._mocks:
            return

        self._mocks.pop(-1)

    @property
    def cast(self) -> T:
        """Helps to avoid type checker mistakes"""
        return cast(T, self)
