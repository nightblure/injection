# Litestar

In order to successfully inject dependencies into Litestar request handlers,
make sure that the following points are completed:
1. use **@inject** decorator **before** http-method Litestar decorator;

2. added for each injected parameter to the request handler a typing of the form
`Union[<your type>, Any]` for Python versions below 3.10 or `<your type> | Any`,

3. use the `Provide` marker from the `injection` (not from Litestar) package indicating the provider

---

## Example

```python3
from typing import Any, Union

from litestar import Litestar, get
from injection import Provide, inject, DeclarativeContainer, providers


class Redis:
    def __init__(self, *, url: str, port: int):
        self.uri = url + ":" + str(port)
        self.url = url
        self.port = port

    def get(self, key):
        return key


class Container(DeclarativeContainer):
    redis = providers.Singleton(
        Redis,
        port=9873,
        url="redis://...",
    )
    num = providers.Object(9402)


@get(
    "/some_resource",
    status_code=200,
)
@inject
async def litestar_endpoint(
    redis: Union[Redis, Any] = Provide[Container.redis],
    num: Union[int, Any] = Provide[Container.num],
) -> dict:
    value = redis.get(800)
    return {"detail": value, "num2": num}


@get(
    "/num_endpoint",
    status_code=200,
)
@inject
async def litestar_endpoint_object_provider(
    num: Union[int, Any] = Provide[Container.num],
) -> dict:
    return {"detail": num}


_handlers = [
    litestar_endpoint,
    litestar_endpoint_object_provider,
]

app = Litestar(route_handlers=_handlers)
```
