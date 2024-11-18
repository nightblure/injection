import asyncio
from dataclasses import dataclass, field

from injection import DeclarativeContainer, Provide, auto_inject, inject, providers


@dataclass
class AnotherSettings:
    some_const = 144


@dataclass
class Settings:
    redis_url: str = "redis://localhost"
    redis_port: int = 6379
    nested_settings: AnotherSettings = field(default_factory=AnotherSettings)


class Redis:
    def __init__(self, *, url: str, port: int):
        self.uri = url + ":" + str(port)
        self.url = url
        self.port = port

    def get(self, key):
        return key


class Service:
    def __init__(self, redis_client: Redis, a=1, b="b"):
        self.redis_client = redis_client
        self.a = a
        self.b = b

    def do_smth(self):
        return "Doing smth"


class SomeService:
    def __init__(self, field: int, redis: Redis, svc: Service):
        self.field = field
        self.redis = redis
        self.svc = svc

    def do_smth(self):
        return "Doing smth 2"


def func(a, *, c: str, nums: int, d: dict):
    _ = a
    _ = c
    _ = d
    return 5555, nums


async def coroutine(arg1, *, arg2):
    await asyncio.sleep(0.1)
    return arg1, arg2


class Container(DeclarativeContainer):
    settings = providers.Singleton(Settings)
    redis = providers.Singleton(
        Redis,
        port=settings.provided.redis_port,
        url=settings.provided.redis_url,
    )
    service = providers.Transient(Service, redis_client=redis)
    some_service = providers.Singleton(SomeService, 1, redis, svc=service)
    num = providers.Object(settings.provided.nested_settings.some_const)
    num2 = providers.Object(9402)
    callable_obj = providers.Callable(func, 1, c="string2", nums=num, d={"d": 500})
    coroutine_provider = providers.Coroutine(coroutine, arg1=1, arg2=2)


@inject
def func_with_injections(
    sfs,
    *,
    ddd,
    redis=Provide[Container.redis],
    svc1=Provide[Container.service],
    svc2=Provide[Container.some_service],
    numms=Provide[Container.num],
):
    _ = sfs
    _ = ddd
    _ = numms

    redis.get(1)
    svc1.do_smth()
    svc2.do_smth()

    return redis.url


@auto_inject
def func_with_auto_injections(
    sfs,
    redis: Redis,
    *,
    ddd,
    svc1: Service,
    svc2: SomeService,
):
    _ = sfs
    _ = ddd

    redis.get(1)
    svc1.do_smth()
    svc2.do_smth()

    return redis.url


@auto_inject
def func_with_auto_injections_mixed(
    sfs,
    *,
    ddd,
    redis: Redis,
    svc1: Service,
    svc2: SomeService,
    numms=Provide[Container.num],
):
    _ = sfs
    _ = ddd
    _ = numms

    redis.get(1)
    svc1.do_smth()
    svc2.do_smth()

    return redis.url
