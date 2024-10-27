from typing import Any, Dict, Tuple, TypeVar, Union

from injection.provided import ProvidedInstance
from injection.providers.base import BaseProvider

T = TypeVar("T")


def resolve_value(
    value: Union[ProvidedInstance, BaseProvider[T], Any],
) -> Union[T, Any]:
    if isinstance(value, ProvidedInstance):
        value = value.get_value()

    if isinstance(value, BaseProvider):
        value = value()

    return value


def get_clean_args(args: Tuple[Any, ...]) -> Tuple[Any, ...]:
    clean_args = []

    for value_or_provider in args:
        resolved_value = resolve_value(value_or_provider)
        clean_args.append(resolved_value)

    return tuple(clean_args)


def get_clean_kwargs(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    clean_kwargs = {}

    for arg, value in kwargs.items():
        clean_kwargs[arg] = resolve_value(value)

    return clean_kwargs
