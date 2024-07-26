from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Any, Generic, Iterator, List, TypeVar

from injection.provided import ProvidedInstance

T = TypeVar("T")


class BaseProvider(Generic[T], ABC):
    def __init__(self):
        self._mocks: List[Any] = []

    @abstractmethod
    def _resolve(self, *args, **kwargs) -> T:
        raise NotImplementedError

    def __call__(self, *args: Any, **kwargs: Any) -> T:
        if self._mocks:
            return self._mocks[-1]
        return self._resolve(*args, **kwargs)

    @property
    def provided(self) -> "ProvidedInstance":
        return ProvidedInstance(provided=self)

    def override(self, mock) -> None:
        self._mocks.append(mock)

    @contextmanager
    def override_context(self, mock) -> Iterator[None]:
        self.override(mock)
        try:
            yield
        finally:
            self.reset_override()

    def reset_override(self) -> None:
        if not self._mocks:
            return

        self._mocks.pop(-1)
