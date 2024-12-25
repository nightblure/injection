import sys
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Generic, Iterator, List, TypeVar, cast

if TYPE_CHECKING:
    pass

if sys.version_info < (3, 10):
    from typing_extensions import ParamSpec
else:
    from typing import ParamSpec

from injection.provided import ProvidedInstance

P = ParamSpec("P")
T = TypeVar("T")


class BaseProvider(Generic[T], ABC):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._args = args
        self._kwargs = kwargs
        self._mocks: List[Any] = []

    @abstractmethod
    def _resolve(self, *args: Any, **kwargs: Any) -> T:
        raise NotImplementedError

    @abstractmethod
    async def _async_resolve(self, *args: Any, **kwargs: Any) -> T:
        raise NotImplementedError

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

    def get_related_providers(self) -> Iterator["BaseProvider[Any]"]:
        for arg in self._args:
            if isinstance(arg, BaseProvider):
                yield arg

        for arg in self._kwargs.values():
            if isinstance(arg, BaseProvider):
                yield arg
