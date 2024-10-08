from injection.providers.callable import Callable
from injection.providers.coroutine import Coroutine
from injection.providers.object import Object
from injection.providers.partial_callable import PartialCallable
from injection.providers.singleton import Singleton
from injection.providers.transient import Transient

__all__ = [
    "Callable",
    "Coroutine",
    "Object",
    "PartialCallable",
    "Singleton",
    "Transient",
]
