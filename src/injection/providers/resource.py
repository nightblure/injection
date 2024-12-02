import inspect
import sys
from contextlib import asynccontextmanager, contextmanager
from typing import (
    Any,
    AsyncContextManager,
    AsyncIterator,
    Callable,
    ContextManager,
    Final,
    Iterator,
    Optional,
    Tuple,
    TypeVar,
    Union,
    cast,
)

from injection.providers.base import BaseProvider

if sys.version_info < (3, 10):
    from typing_extensions import ParamSpec
else:
    from typing import ParamSpec

P = ParamSpec("P")
T = TypeVar("T")


def _create_context_factory(
    context_factory: Callable[
        P,
        Union[
            Iterator[T],
            AsyncIterator[T],
            ContextManager[T],
            AsyncContextManager[T],
        ],
    ],
) -> Tuple[Any, bool]:
    context: Any = None
    async_mode: bool = False

    if inspect.isasyncgenfunction(context_factory):
        async_mode = True
        context = asynccontextmanager(context_factory)
    elif inspect.isgeneratorfunction(context_factory):
        context = contextmanager(context_factory)
    elif isinstance(context_factory, type) and issubclass(
        context_factory,
        ContextManager,
    ):
        context = context_factory
    elif isinstance(context_factory, type) and issubclass(
        context_factory,
        AsyncContextManager,
    ):
        async_mode = True
        context = context_factory
    else:
        src_code = inspect.getsource(context_factory)
        async_mode = "@asynccontextmanager" in src_code

        if "@contextmanager" in src_code or "@asynccontextmanager" in src_code:
            return context_factory, async_mode

        msg = f"Unsupported resource factory type {str(type(context_factory))!r}"
        raise RuntimeError(msg)

    return context, async_mode


_resource_not_initialized_error_msg: Final[str] = "Resource is not initialized"


class Resource(BaseProvider[T]):
    def __init__(  # type: ignore[valid-type]
        self,
        factory: Callable[
            P,
            Union[
                Iterator[T],
                AsyncIterator[T],
                ContextManager[T],
                AsyncContextManager[T],
            ],
        ],
        *args: P.args,
        function_scope: bool = False,
        **kwargs: P.kwargs,
    ) -> None:
        super().__init__()
        self._context_factory, self._async_mode = _create_context_factory(factory)

        self._context: Any = None

        self._args = args
        self._kwargs = kwargs
        self._factory = factory

        self._initialized = False
        self._instance: Optional[T] = None
        self._function_scope = function_scope

    def __create_context(self) -> None:
        self._context = self._context_factory(*self._args, **self._kwargs)

    def reset(self) -> None:
        self._context = None
        self._initialized = False

    @property
    def initialized(self) -> bool:
        return self._initialized

    @property
    def function_scope(self) -> bool:
        return self._function_scope

    @property
    def async_mode(self) -> bool:
        return self._async_mode

    @property
    def instance(self) -> T:
        return cast(T, self._instance)

    def _resolve(self) -> T:
        if self.initialized:
            return self.instance

        self.__create_context()
        self._instance = self._context.__enter__()
        self._initialized = True
        return self.instance

    def close(self) -> None:
        if not self._initialized:
            raise RuntimeError(_resource_not_initialized_error_msg)

        self._context.__exit__(None, None, None)
        self.reset()

    async def _async_resolve(self) -> T:
        if self.initialized:
            return self.instance

        self.__create_context()

        if self.async_mode:
            self._instance = await self._context.__aenter__()
        else:
            self._instance = self._context.__enter__()

        self._initialized = True
        return self.instance

    async def async_close(self) -> None:
        if not self._initialized:
            raise RuntimeError(_resource_not_initialized_error_msg)

        await self._context.__aexit__(None, None, None)
        self.reset()
