import asyncio
from dataclasses import dataclass, field

from injection import DeclarativeContainer, Provide, inject, providers


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
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

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
    partial_callable = providers.PartialCallable(func, 1, c="string", nums=num)
    callable_obj = providers.Callable(func, 1, c="string2", nums=num, d={"d": 500})
    transient_obj = providers.Transient(
        Redis,
        port=settings.provided.redis_port,
        url=settings.provided.redis_url,
    )
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
    partial_callable_param=Provide[Container.partial_callable],
):
    _ = sfs
    _ = ddd
    _ = numms

    redis.get(1)
    svc1.do_smth()
    svc2.do_smth()

    partial_callable_result = partial_callable_param(d={"eparam": "eeeee"})
    _ = partial_callable_result
    return redis.url
