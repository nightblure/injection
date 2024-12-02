from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Iterator, Tuple

from injection import DeclarativeContainer, Provide, auto_inject, inject, providers


class Resources:
    def __init__(self) -> None:
        self._value: int = 100
        self.closed = True
        self.active = False

    def sync_generator(self) -> Iterator["Resources"]:
        self.active = True
        self.closed = False
        yield self
        self.active = False
        self.closed = True

    async def async_generator(self) -> AsyncIterator["Resources"]:
        self.active = True
        self.closed = False
        yield self
        self.active = False
        self.closed = True

    @contextmanager
    def sync_ctx(self) -> Iterator["Resources"]:
        self.active = True
        self.closed = False
        yield self
        self.active = False
        self.closed = True

    @asynccontextmanager
    async def async_ctx(self) -> AsyncIterator["Resources"]:
        self.active = True
        self.closed = False
        yield self
        self.active = False
        self.closed = True

    def set_value(self, value: int) -> None:
        self._value = value


@dataclass
class AnotherSettings:
    some_const: int = 144


@dataclass
class Settings:
    redis_url: str = "redis://localhost"
    redis_port: int = 6379
    nested_settings: AnotherSettings = field(default_factory=AnotherSettings)


class Redis:
    def __init__(self, *, url: str, port: int) -> None:
        self.uri = url + ":" + str(port)
        self.url = url
        self.port = port

    def get(self, key: Any) -> Any:
        return key


class Service:
    def __init__(self, redis_client: Redis, a: int, b: str) -> None:
        self.redis_client = redis_client
        self.a = a
        self.b = b

    def do_smth(self) -> str:
        return "Doing smth"


class SomeService:
    def __init__(self, f: int, redis: Redis, svc: Service) -> None:
        self.field = f
        self.svc = svc
        self.redis = redis

    def do_smth(self) -> str:
        return "Doing smth 2"


async def coroutine(arg1: int, *, arg2: int) -> Tuple[int, int]:
    return arg1, arg2


async def async_dependency_provider_func(
    value: int,
    coro_result_positional: Tuple[int, int],
    *,
    coro_result: Tuple[int, int],
    nested_coro_provider: Tuple[
        Tuple[int, int],
        Tuple[int, int],
        int,
    ],
) -> Tuple[
    int,
    Tuple[int, int],
    Tuple[int, int],
    Tuple[
        Tuple[int, int],
        Tuple[int, int],
        int,
    ],
]:
    return (
        value,
        coro_result,
        coro_result_positional,
        nested_coro_provider,
    )


async def nested_coroutine(
    arg1: Tuple[int, int],
    arg2: Tuple[int, int],
    arg3: int,
) -> Tuple[
    Tuple[int, int],
    Tuple[int, int],
    int,
]:
    return arg1, arg2, arg3


# def _sync_resource_simple() -> Iterator[str]:
#     yield "sync_resource_simple"


class Container(DeclarativeContainer):
    settings = providers.Singleton(Settings)
    redis = providers.Singleton(
        Redis,
        port=settings.provided.redis_port,  # type: ignore[arg-type]
        url=settings.provided.redis_url,  # type: ignore[arg-type]
    )
    service = providers.Transient(Service, redis_client=redis.cast, a=1, b="b")
    some_service = providers.Singleton(SomeService, 1, redis.cast, svc=service.cast)
    num = providers.Object(1234)
    num2 = providers.Object(9402)
    coroutine_provider = providers.Coroutine(coroutine, arg1=1, arg2=2)

    sync_func_with_coro_dependency = providers.Factory(
        lambda a: a,
        coroutine_provider,
    )

    nested_coro_provider = providers.Coroutine(
        nested_coroutine,
        coroutine_provider.cast,
        arg2=coroutine_provider.cast,
        arg3=settings.provided.nested_settings.some_const,  # type: ignore[arg-type]
    )

    async_dependency_provider = providers.Coroutine(
        async_dependency_provider_func,
        1778,
        coroutine_provider.cast,
        coro_result=coroutine_provider.cast,
        nested_coro_provider=nested_coro_provider.cast,
    )

    sync_resource = providers.Resource(
        Resources().sync_generator,
    )

    sync_resource_func_scope = providers.Resource(
        Resources().sync_ctx,
        function_scope=True,
    )

    async_resource = providers.Resource(
        Resources().async_generator,
    )

    async_resource_func_scope = providers.Resource(
        Resources().async_ctx,
        function_scope=True,
    )

    sync_func_with_async_resource_dependency = providers.Factory(
        lambda a: a,
        async_resource,
    )


@inject
def func_with_injections(
    sfs: Any,
    *,
    ddd: Any,
    redis: Redis = Provide[Container.redis],
    svc1: Service = Provide[Container.service],
    svc2: SomeService = Provide[Container.some_service],
    numms: int = Provide[Container.num],
) -> str:
    _ = sfs
    _ = ddd
    _ = numms

    redis.get(1)
    svc1.do_smth()
    svc2.do_smth()

    return redis.url


@auto_inject(target_container=Container)
def func_with_auto_injections(
    sfs: Any,
    redis: Redis,
    *,
    ddd: Any,
    svc1: Service,
    svc2: SomeService,
) -> str:
    _ = sfs
    _ = ddd

    redis.get(1)
    svc1.do_smth()
    svc2.do_smth()

    return redis.url


@auto_inject(target_container=Container)
def func_with_auto_injections_mixed(
    sfs: Any,
    *,
    ddd: Any,
    redis: Redis,
    svc1: Service,
    svc2: SomeService,
    numms: int = Provide[Container.num],
    coro_value: Tuple[int, int] = Provide[Container.coroutine_provider],
) -> str:
    _ = sfs
    _ = ddd
    _ = numms

    redis.get(1)
    svc1.do_smth()
    svc2.do_smth()

    assert coro_value == (1, 2)

    return redis.url
