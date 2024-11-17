from typing import Any, Callable, Optional, TypeVar, cast

from typing_extensions import ParamSpec

from injection.providers.base_factory import BaseFactoryProvider

P = ParamSpec("P")
T = TypeVar("T")


class Singleton(BaseFactoryProvider[T]):
    """Global singleton object created only once"""

    def __init__(self, type_cls: Callable[P, T], *a: Any, **kw: Any) -> None:
        super().__init__(type_cls, *a, **kw)
        self.type_cls = type_cls
        self._instance: Optional[T] = None

    def _resolve(self, *args: Any, **kwargs: Any) -> T:
        """https://python-dependency-injector.ets-labs.org/providers/factory.html

        Positional arguments are appended after Factory positional dependencies.
        Keyword arguments have the priority over the Factory keyword dependencies with the same name.
        """

        if self._instance is None:
            instance = super()._resolve(*args, **kwargs)
            self._instance = cast(T, instance)

        return self._instance

    def reset(self) -> None:
        self._instance = None
