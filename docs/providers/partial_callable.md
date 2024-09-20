# Partial callable

**Partial callable** it is a provider very similar in principle to the mechanics of the callable provider,
but works a bit differently and allows for flexibility in some specific situations.

Let's imagine that we are in a case when we know some values of parameters of a future object right now,
but some values will be known in the future (in runtime).
Obviously, resolving such a provider will not make any sense until the values of all its parameters are known.
But this provider allows you to flexibly fix the values of previously known parameters of the future object,
and the remaining values can be passed at the moment when these values are determined.

## Example
```python3
from injection.providers import PartialCallable


def some_function(a: str, b: int, *, c: str):
    return a, b, c


if __name__ == '__main__':
    provider = PartialCallable(some_function, 1, 99)
    callable_object = provider()
    assert callable_object(c=5) == (1, 99, 5)
```
