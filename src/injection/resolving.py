from typing import Any, Dict, List, Tuple, TypeVar, Union

from injection.provided import ProvidedInstance
from injection.providers.base import BaseProvider

T = TypeVar("T")


def _resolve_value(
    value: Union[ProvidedInstance, BaseProvider[T], Any],
) -> Any:
    if isinstance(value, ProvidedInstance):
        value = value.get_value()

    if isinstance(value, BaseProvider):
        value = value()

    return value


async def _resolve_value_async(
    value: Union[ProvidedInstance, BaseProvider[T], Any],
) -> Any:
    if isinstance(value, ProvidedInstance):
        value = value.get_value()

    if isinstance(value, BaseProvider):
        value = await value.async_resolve()

    return value


def _resolve_positional_args(*args: Any) -> List[Any]:
    clean_args = []

    for value_or_provider in args:
        resolved_value = _resolve_value(value_or_provider)
        clean_args.append(resolved_value)

    return clean_args


def _resolve_kwargs(**kwargs: Any) -> Dict[str, Any]:
    clean_kwargs = {}

    for arg, value in kwargs.items():
        resolved_value = _resolve_value(value)
        clean_kwargs[arg] = resolved_value

    return clean_kwargs


async def _resolve_positional_args_async(*args: Any) -> List[Any]:
    resolved_args = []

    for value_or_provider in args:
        resolved_value = await _resolve_value_async(value_or_provider)
        resolved_args.append(resolved_value)

    return resolved_args


async def _resolve_kwargs_async(**kwargs: Any) -> Dict[str, Any]:
    resolved_kwargs = {}

    for arg, value_or_provider in kwargs.items():
        resolved_value = await _resolve_value_async(value_or_provider)
        resolved_kwargs[arg] = resolved_value

    return resolved_kwargs


def resolve_provider_args(
    *args: Any,
    **kwargs: Any,
) -> Tuple[List[Any], Dict[str, Any]]:
    resolved_args = _resolve_positional_args(*args)
    resolved_kwargs = _resolve_kwargs(**kwargs)
    return resolved_args, resolved_kwargs


async def resolve_provider_args_async(
    *args: Any,
    **kwargs: Any,
) -> Tuple[List[Any], Dict[str, Any]]:
    resolved_args = await _resolve_positional_args_async(*args)
    resolved_kwargs = await _resolve_kwargs_async(**kwargs)
    return resolved_args, resolved_kwargs
