import inspect
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Tuple,
    TypeVar,
    Union,
    cast,
)

from typing_extensions import ParamSpec

from injection.providers.base import BaseProvider
from injection.resolving import get_clean_args, get_clean_kwargs

P = ParamSpec("P")
T = TypeVar("T")


class BaseFactoryProvider(BaseProvider[T]):
    def __init__(
        self,
        factory: Union[Callable[P, Awaitable[T]], Callable[P, T]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> None:
        super().__init__()
        self._args = args
        self._kwargs = kwargs
        self._factory = factory

    def _get_final_args_and_kwargs(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Tuple[Tuple[Any, ...], Dict[str, Any]]:
        clean_args = get_clean_args(self._args)
        clean_kwargs = get_clean_kwargs(self._kwargs)

        # Common solution for bug when litestar try to add kwargs with name 'args' and 'kwargs'
        if len(args) > 0 or len(kwargs) > 0:
            type_cls_init_signature = inspect.signature(self._factory)
            parameters = type_cls_init_signature.parameters

            args = tuple(arg for arg in args if arg in parameters)
            kwargs = {arg: value for arg, value in kwargs.items() if arg in parameters}

        final_args: List[Any] = []
        final_args.extend(clean_args)
        final_args.extend(args)

        final_kwargs: Dict[str, Any] = {}
        final_kwargs.update(clean_kwargs)
        final_kwargs.update(kwargs)
        return tuple(final_args), final_kwargs

    def _resolve(self, *args: Any, **kwargs: Any) -> Union[Callable[P, T], T]:
        """
        Positional arguments are appended after Factory positional dependencies.
        Keyword arguments have the priority over the Factory keyword dependencies with the same name.
        """
        final_args, final_kwargs = self._get_final_args_and_kwargs(*args, **kwargs)
        instance = cast(Callable[P, T], self._factory(*final_args, **final_kwargs))
        return instance
