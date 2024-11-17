import pytest
from litestar import Litestar, get
from litestar.di import Provide
from litestar.testing import TestClient

from injection import inject
from tests.container_objects import Container, Redis


@get(
    "/some_resource",
    status_code=200,
    dependencies={"redis": Provide(Container.redis)},
)
@inject
async def litestar_endpoint_with_direct_provider_injection(redis: Redis) -> dict:
    value = redis.get(800)
    return {"detail": value}


@get(
    "/num_endpoint",
    status_code=200,
    dependencies={"num": Provide(Container.num2)},
)
async def litestar_endpoint_object_provider(num: int) -> dict:
    return {"detail": num}


_handlers = [
    litestar_endpoint_object_provider,
    litestar_endpoint_with_direct_provider_injection,
]

app_deps = {
    # "redis": Provide(Container.redis),
}

app = Litestar(route_handlers=_handlers, debug=True, dependencies=app_deps)


@pytest.mark.xfail(
    reason="TypeError: __init__() got an unexpected keyword argument 'args'",
)
def test_litestar_endpoint_with_direct_provider_injection():
    with TestClient(app=app) as client:
        response = client.get("/some_resource")

    assert response.status_code == 200
    assert response.json() == {"detail": 800}


def test_litestar_object_provider():
    with TestClient(app=app) as client:
        response = client.get("/num_endpoint")

    assert response.status_code == 200
    assert response.json() == {"detail": 9402}


class _RedisMock:
    def get(self, _):
        return 192342526


@pytest.mark.xfail(
    reason="TypeError: Unsupported type: <class 'tests.integration.test_litestar.test_integration._RedisMock'>",
)
def test_litestar_overriding_direct_provider_endpoint():
    mock_instance = _RedisMock()

    with TestClient(app=app) as client:
        with Container.redis.override_context(mock_instance):
            response = client.get("/some_resource")

    assert response.status_code == 200
    assert response.json() == {"detail": 192342526}
