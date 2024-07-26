from injection import providers


def some_function(a: str, b: int, *, c: str):
    return a, b, c


def test_callable_with_only_kwargs():
    kwargs = {"a": "aa", "b": 22, "c": "ccc"}
    callable_provider = providers.Callable(some_function, **kwargs)
    assert tuple(kwargs.values()) == callable_provider()


def test_callable_with_positional_args_and_kwargs():
    args = ["aasgsg,", 221]
    kwargs = {"c": "csfsfcc"}
    callable_provider = providers.Callable(some_function, *args, **kwargs)

    values = []
    values.extend(args)
    values.extend(kwargs.values())
    assert tuple(values) == callable_provider()


def test_callable_with_args_override():
    kwargs = {"a": "aa", "b": 22, "c": "ccc"}
    callable_provider = providers.Callable(some_function, **kwargs)
    assert callable_provider(a="new_a", c="new_value") == ("new_a", 22, "new_value")
    assert tuple(kwargs.values()) == callable_provider()
