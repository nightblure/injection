import inspect
from typing import Type, TypeVar

from injection.providers.base import BaseProvider
from injection.resolving import get_clean_args, get_clean_kwargs

T = TypeVar("T")


class Transient(BaseProvider[T]):
    """Object that needs to be created every time"""

    def __init__(self, type_cls: Type[T], *a, **kw):
        super().__init__()
        self.type_cls = type_cls
        self.args = a
        self.kwargs = kw
        self._instance = None

    def _resolve(self, *args, **kwargs) -> T:
        """https://python-dependency-injector.ets-labs.org/providers/factory.html

        Positional arguments are appended after Factory positional dependencies.
        Keyword arguments have the priority over the Factory keyword dependencies with the same name.
        """
        clean_args = get_clean_args(self.args)
        clean_kwargs = get_clean_kwargs(self.kwargs)

        # Common solution for bug when litestar try to add kwargs with name 'args' and 'kwargs'
        if len(args) > 0 or len(kwargs) > 0:
            type_cls_init_signature = inspect.signature(self.type_cls)
            parameters = type_cls_init_signature.parameters

            args = [arg for arg in args if arg in parameters]
            kwargs = {arg: value for arg, value in kwargs.items() if arg in parameters}

        final_args = []
        final_args.extend(clean_args)
        final_args.extend(args)

        final_kwargs = {}
        final_kwargs.update(clean_kwargs)
        final_kwargs.update(kwargs)

        instance = self.type_cls(*final_args, **final_kwargs)
        return instance
