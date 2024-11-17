from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Tuple,
    TypeVar,
    Union,
)

from typing_extensions import ParamSpec

from injection.providers.base import BaseProvider
from injection.resolving import get_clean_args, get_clean_kwargs

P = ParamSpec("P")
T = TypeVar("T")


class BaseFactoryProvider(BaseProvider[T]):
    def __init__(
        self,
        factory: Callable[P, T],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> None:
        super().__init__()
        self._args = args
        self._kwargs = kwargs
        self._factory = factory

    @property
    def factory(self) -> Callable[P, T]:
        return self._factory  # type: ignore

    def _get_final_args_and_kwargs(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Tuple[Tuple[Any, ...], Dict[str, Any]]:
        clean_args = get_clean_args(self._args)
        clean_kwargs = get_clean_kwargs(self._kwargs)

        final_args: List[Any] = []
        final_args.extend(clean_args)
        final_args.extend(args)

        final_kwargs: Dict[str, Any] = {}
        final_kwargs.update(clean_kwargs)
        final_kwargs.update(kwargs)
        return tuple(final_args), final_kwargs

    def _resolve(self, *args: Any, **kwargs: Any) -> Union[T, Awaitable[T]]:
        """
        Positional arguments are appended after Factory positional dependencies.
        Keyword arguments have the priority over the Factory keyword dependencies with the same name.
        """
        final_args, final_kwargs = self._get_final_args_and_kwargs(*args, **kwargs)
        instance = self._factory(*final_args, **final_kwargs)
        return instance
