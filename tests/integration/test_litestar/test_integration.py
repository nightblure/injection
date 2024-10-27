from typing import Any

from litestar import Litestar, post
from litestar.di import Provide
from litestar.testing import TestClient

from tests.container_objects import Container


@post(
    "/some_resource",
    status_code=200,
    dependencies={"redis": Provide(Container.redis)},
)
async def some_litestar_endpoint(redis: Any) -> dict:
    value = redis.get(-924)
    return {"detail": value}


app = Litestar(route_handlers=[some_litestar_endpoint], pdb_on_exception=True)


def test_litestar_endpoint():
    with TestClient(app=app) as client:
        response = client.post("/some_resource")
        assert response.status_code == 200
        assert response.json() == {"detail": -924}


def test_litestar_endpoint_with_overriding():
    class RedisMock:
        def get(self, _):
            return 1119

    mock_redis = RedisMock()

    with TestClient(app=app) as client:
        with Container.redis.override_context(mock_redis):
            response = client.post("/some_resource")

    assert response.status_code == 200
    assert response.json() == {"detail": 1119}
