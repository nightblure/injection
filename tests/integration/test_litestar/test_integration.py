import pytest
from litestar import Litestar, get
from litestar.di import Provide
from litestar.testing import TestClient

# from injection import Provide
from tests.container_objects import Container, Redis


@get(
    "/some_resource",
    status_code=200,
    dependencies={"redis": Provide(Container.redis)},
)
async def litestar_endpoint_with_direct_provider_injection(redis: Redis) -> dict:
    value = redis.get(800)
    return {"detail": value}


@get(
    "/num_endpoint",
    status_code=200,
    dependencies={"num": Provide(Container.num2)},
)
async def litestar_num_endpoint(num: int) -> dict:
    return {"detail": num}


_handlers = [
    litestar_endpoint_with_direct_provider_injection,
    litestar_num_endpoint,
]

app = Litestar(route_handlers=_handlers, pdb_on_exception=True)


@pytest.mark.xfail(
    reason="litestar error - TypeError: __init__() got an unexpected keyword argument 'args'",
)
def test_litestar_endpoint_with_direct_provider_injection():
    with TestClient(app=app) as client:
        response = client.get("/some_resource")

    assert response.status_code == 200
    assert response.json() == {"detail": 800}


@pytest.mark.xfail(reason="unknown")
def test_litestar_num_endpoint():
    with TestClient(app=app) as client:
        response = client.get("/num_endpoint")

    assert response.status_code == 200
    assert response.json() == {"detail": 9402}


class _RedisMock:
    def get(self, _):
        return 192342526


@pytest.mark.xfail(reason="unknown")
def test_litestar_overriding_direct_provider_endpoint():
    with TestClient(app=app) as client:
        with Container.redis.override_context(_RedisMock()):
            response = client.get("/some_resource")

    assert response.status_code == 200
    assert response.json() == {"detail": 192342526}
