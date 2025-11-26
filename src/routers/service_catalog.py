from fastapi import APIRouter, Body, Depends
from ..controllers.service_catalog import (
    get_all_service_catalogs,
    get_service_catalog,
    create_service_catalogs,
    update_service_catalogs,
    delete_service_catalogs,
)
from ..schemas.service_catalog import (
    ServiceCatalogCreate,
    ServiceCatalogBulkUpdate,
    ServiceCatalogResponse,
    ServiceCatalogListResponse,
)
from ..lib.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=ServiceCatalogListResponse)
async def read_all_service_catalogs(user_id: int = Depends(get_current_user)):
    """Get all service catalogs"""
    return await get_all_service_catalogs()


@router.get("/{catalog_id}", response_model=ServiceCatalogResponse)
async def read_service_catalog(
    catalog_id: int, user_id: int = Depends(get_current_user)
):
    """Get a specific service catalog by ID"""
    return await get_service_catalog(catalog_id)


@router.post("/", response_model=list[ServiceCatalogResponse], status_code=201)
async def create_service_catalogs_endpoint(
    catalogs_data: list[ServiceCatalogCreate],
    user_id: int = Depends(get_current_user),
):
    """Create multiple service catalogs in bulk"""
    return await create_service_catalogs(catalogs_data)


@router.put("/", response_model=list[ServiceCatalogResponse])
async def update_service_catalogs_endpoint(
    catalogs_data: list[ServiceCatalogBulkUpdate] = Body(...),
    user_id: int = Depends(get_current_user),
):
    """Update multiple service catalogs in bulk. Each item should contain 'id' and fields to update."""
    return await update_service_catalogs(catalogs_data)


@router.delete("/")
async def delete_service_catalogs_endpoint(
    catalog_ids: list[int] = Body(..., embed=True),
    user_id: int = Depends(get_current_user),
):
    """Delete multiple service catalogs"""
    return await delete_service_catalogs(catalog_ids)
