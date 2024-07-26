import inspect
from typing import Any, Callable, Dict, Tuple, Type, TypeVar, Union

from injection.providers.base import BaseProvider
from injection.resolving import get_clean_args, get_clean_kwargs

T = TypeVar("T")
FactoryType = Union[Type[T], Callable[..., T]]


class BaseFactoryProvider(BaseProvider[T]):
    def __init__(self, factory: FactoryType, *args, **kwargs) -> None:
        super().__init__()
        self._factory = factory
        self._args = args
        self._kwargs = kwargs

    def _get_final_args_and_kwargs(
        self,
        *args,
        **kwargs,
    ) -> Tuple[Tuple[Any, ...], Dict[str, Any]]:
        clean_args = get_clean_args(self._args)
        clean_kwargs = get_clean_kwargs(self._kwargs)

        # Common solution for bug when litestar try to add kwargs with name 'args' and 'kwargs'
        if len(args) > 0 or len(kwargs) > 0:
            type_cls_init_signature = inspect.signature(self._factory)
            parameters = type_cls_init_signature.parameters

            args = [arg for arg in args if arg in parameters]
            kwargs = {arg: value for arg, value in kwargs.items() if arg in parameters}

        final_args = []
        final_args.extend(clean_args)
        final_args.extend(args)

        final_kwargs: Dict[str, Any] = {}
        final_kwargs.update(clean_kwargs)
        final_kwargs.update(kwargs)
        return tuple(final_args), final_kwargs

    def _resolve(self, *args, **kwargs) -> T:
        """https://python-dependency-injector.ets-labs.org/providers/factory.html

        Positional arguments are appended after Factory positional dependencies.
        Keyword arguments have the priority over the Factory keyword dependencies with the same name.
        """
        final_args, final_kwargs = self._get_final_args_and_kwargs(*args, **kwargs)
        instance = self._factory(*final_args, **final_kwargs)
        return instance
