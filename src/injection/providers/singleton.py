from typing import Any, Optional, Type, TypeVar, cast

from injection.providers.base_factory import BaseFactoryProvider

T = TypeVar("T")


class Singleton(BaseFactoryProvider[T]):
    """Global singleton object created only once"""

    def __init__(self, type_cls: Type[T], *a: Any, **kw: Any) -> None:
        super().__init__(type_cls, *a, **kw)
        self._instance: Optional[T] = None
        self.type_cls = type_cls

    def _resolve(self, *args: Any, **kwargs: Any) -> T:
        """https://python-dependency-injector.ets-labs.org/providers/factory.html

        Positional arguments are appended after Factory positional dependencies.
        Keyword arguments have the priority over the Factory keyword dependencies with the same name.
        """

        if self._instance is None:
            self._instance = cast(T, super()._resolve(*args, **kwargs))

        return self._instance

    def reset(self) -> None:
        self._instance = None
