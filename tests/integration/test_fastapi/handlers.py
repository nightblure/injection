import sys

if sys.version_info >= (3, 9):
    from typing import Annotated
else:
    from typing_extensions import Annotated

from fastapi import APIRouter, Depends

from injection import Provide, inject
from tests.container_objects import Container, Redis

router = APIRouter(prefix="/api")

RedisDependency = Annotated[Redis, Depends(Provide[Container.redis])]
RedisDependencyWithoutProvideMarker = Annotated[Redis, Depends(Container.redis)]


@router.get("/values")
@inject
def some_get_endpoint_handler(redis: RedisDependency):
    value = redis.get(299)
    return {"detail": value}


@router.post("/values")
@inject
async def some_get_async_endpoint_handler(redis: RedisDependency):
    value = redis.get(399)
    return {"detail": value}


@router.post("/values-without_provide")
@inject
async def async_endpoint_handler_with_dep_without_provide(
    _: RedisDependencyWithoutProvideMarker,
): ...
