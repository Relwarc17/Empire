from datetime import datetime

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from empire.server.common.module_models import PydanticModule
from empire.server.server import main
from empire.server.v2.api.EmpireApiRouter import APIRouter
from empire.server.v2.api.jwt_auth import get_current_active_user
from empire.server.v2.api.module.module_dto import (
    Module,
    ModuleBulkUpdateRequest,
    Modules,
    ModuleUpdateRequest,
    domain_to_dto_module,
)
from empire.server.v2.api.shared_dependencies import get_db

module_service = main.modulesv2

router = APIRouter(
    prefix="/api/v2beta/modules",
    tags=["modules"],
    responses={404: {"description": "Not found"}},
)


async def get_module(uid: str):
    module = module_service.get_by_id(uid)

    if module:
        return module

    raise HTTPException(status_code=404, detail=f"Module not found for id {uid}")


@router.get(
    "/",
    # todo is there an equivalent for this that doesn't cause fastapi to convert the object twice?
    #  Still want to display the response type in the docs
    # response_model=Modules,
    dependencies=[Depends(get_current_active_user)],
)
async def read_modules():
    print(f"Request Received {datetime.utcnow()}")
    modules = list(
        map(
            lambda x: domain_to_dto_module(x[1], x[0]), module_service.get_all().items()
        )
    )

    print(f"Done Converting Objects {datetime.utcnow()}")

    return {"records": modules}


@router.get(
    "/{uid}", response_model=Module, dependencies=[Depends(get_current_active_user)]
)
async def read_module(uid: str, module: PydanticModule = Depends(get_module)):
    return domain_to_dto_module(module, uid)


@router.put(
    "/{uid}", response_model=Module, dependencies=[Depends(get_current_active_user)]
)
async def update_module(
    uid: str,
    module_req: ModuleUpdateRequest,
    module: PydanticModule = Depends(get_module),
    db: Session = Depends(get_db),
):
    module_service.update_module(db, module, module_req)

    return domain_to_dto_module(module, uid)


@router.put(
    "/bulk/enable", status_code=204, dependencies=[Depends(get_current_active_user)]
)
async def update_bulk_enable(
    module_req: ModuleBulkUpdateRequest, db: Session = Depends(get_db)
):
    module_service.update_modules(db, module_req)
