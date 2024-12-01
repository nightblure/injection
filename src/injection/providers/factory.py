import sys
from typing import Callable, TypeVar

from injection.providers.base_factory import BaseFactoryProvider

if sys.version_info < (3, 10):
    from typing_extensions import ParamSpec
else:
    from typing import ParamSpec

P = ParamSpec("P")
T = TypeVar("T")


class Factory(BaseFactoryProvider[T]):
    """Object that needs to be created every time"""

    def __init__(
        self,
        factory: Callable[P, T],
        *a: P.args,
        **kw: P.kwargs,
    ) -> None:
        super().__init__(factory, *a, **kw)
