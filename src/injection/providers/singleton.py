from typing import Type, TypeVar

from injection.providers.base_factory import BaseFactoryProvider

T = TypeVar("T")


class Singleton(BaseFactoryProvider[T]):
    """Global singleton object created only once"""

    def __init__(self, type_cls: Type[T], *a, **kw):
        super().__init__(type_cls, *a, **kw)
        self._instance = None
        self.type_cls = type_cls

    def _resolve(self, *args, **kwargs) -> T:
        """https://python-dependency-injector.ets-labs.org/providers/factory.html

        Positional arguments are appended after Factory positional dependencies.
        Keyword arguments have the priority over the Factory keyword dependencies with the same name.
        """
        if args or kwargs:
            self.reset_cache()

        if self._instance is None:
            self._instance = super()._resolve(*args, **kwargs)

        return self._instance

    def reset_cache(self):
        self._instance = None
