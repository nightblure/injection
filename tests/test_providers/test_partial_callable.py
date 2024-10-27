import functools

import pytest

from injection import providers


def some_function(a: str, b: int, *, c: str):
    return a, b, c


def test_partial_callable_resolving_fail_without_arg():
    kwargs = {"a": "aa", "b": 22}
    callable_provider = providers.PartialCallable(some_function, **kwargs)

    with pytest.raises(TypeError) as e:
        callable_provider()()

    match = "some_function() missing 1 required keyword-only argument: 'c'"
    assert e.value.args[0] == match


def test_partial_callable_resolving():
    args = ("aa", 22)
    kwargs = {"c": "value"}
    provider = providers.PartialCallable(some_function, *args)
    resolved_callable = provider(**kwargs)

    assert isinstance(resolved_callable, functools.partial)
    assert resolved_callable.args == args
    assert resolved_callable.keywords == kwargs
    assert tuple([*args, "value"]) == resolved_callable()
