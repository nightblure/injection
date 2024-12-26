import sys
from typing import Any, Dict

from tests.integration.conftest import SomeDAO, SqlaResourceContainer

if sys.version_info >= (3, 9):
    from typing import Annotated
else:
    from typing_extensions import Annotated

from fastapi import APIRouter, Depends

from injection import Provide, inject

router = APIRouter(prefix="/sqlalchemy-resources")


SomeDAODependency = Annotated[SomeDAO, Depends(Provide[SqlaResourceContainer.some_dao])]


@router.get("/sync/{value}")
@inject
def sqla_resource_handler_sync(
    some_dao: SomeDAODependency,
    value: int,
) -> Dict[str, Any]:
    value = some_dao.get_some_data(num=value)
    return {"detail": value}


@router.get("/async/{value}")
@inject
async def sqla_resource_handler_async(
    some_dao: SomeDAODependency,
    value: int,
) -> Dict[str, Any]:
    value = some_dao.get_some_data(num=value)
    return {"detail": value}
