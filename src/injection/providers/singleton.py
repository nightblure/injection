from typing import Type, TypeVar

from injection.providers.transient import Transient

T = TypeVar("T")


class Singleton(Transient[T]):
    """Global singleton object created only once"""

    def __init__(self, type_cls: Type[T], *a, **kw):
        super().__init__(type_cls, *a, **kw)

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
