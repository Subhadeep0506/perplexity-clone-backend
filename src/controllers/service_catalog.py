from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DBAPIError
from fastapi import HTTPException
from ..database.database import session_pool, DatabaseConnectionError
from ..models.service_catalog import ServiceCatalog
from ..schemas.service_catalog import (
    ServiceCatalogCreate,
    ServiceCatalogBulkUpdate,
    ServiceCatalogResponse,
    ServiceCatalogListResponse,
)
from ..services.logger import SingletonLogger

logger = SingletonLogger().get_logger()


async def get_all_service_catalogs() -> ServiceCatalogListResponse:
    """Get all service catalogs"""
    try:
        async with session_pool() as session:
            result = await session.execute(select(ServiceCatalog))
            catalogs = result.scalars().all()
            services = [
                ServiceCatalogResponse.model_validate(catalog) for catalog in catalogs
            ]
            return ServiceCatalogListResponse(services=services)
    except DBAPIError as e:
        logger.exception(
            f"Database connection error fetching service catalogs: {str(e)}"
        )
        raise DatabaseConnectionError(str(e))
    except SQLAlchemyError as e:
        logger.error(f"Database error fetching service catalogs: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve service catalogs"
        )
    except Exception as e:
        logger.error(f"Unexpected error fetching service catalogs: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def get_service_catalog(catalog_id: int) -> ServiceCatalogResponse:
    """Get a specific service catalog by ID"""
    try:
        async with session_pool() as session:
            result = await session.execute(
                select(ServiceCatalog).where(ServiceCatalog.id == catalog_id)
            )
            catalog = result.scalar_one_or_none()
            if not catalog:
                logger.warning(f"Service catalog not found: catalog_id={catalog_id}")
                raise HTTPException(status_code=404, detail="Service catalog not found")
            return ServiceCatalogResponse.model_validate(catalog)
    except HTTPException:
        raise
    except DBAPIError as e:
        logger.exception(
            f"Database connection error fetching service catalog catalog_id={catalog_id}: {str(e)}"
        )
        raise DatabaseConnectionError(str(e))
    except SQLAlchemyError as e:
        logger.error(
            f"Database error fetching service catalog catalog_id={catalog_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=500, detail="Failed to retrieve service catalog"
        )
    except Exception as e:
        logger.error(
            f"Unexpected error fetching service catalog catalog_id={catalog_id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Internal server error")


async def create_service_catalogs(
    catalogs_data: list[ServiceCatalogCreate],
) -> list[ServiceCatalogResponse]:
    """Create multiple service catalogs in bulk"""
    try:
        async with session_pool() as session:
            created_catalogs = []
            errors = []

            for idx, catalog_data in enumerate(catalogs_data):
                try:
                    # Check if slug already exists
                    result = await session.execute(
                        select(ServiceCatalog).where(
                            ServiceCatalog.slug == catalog_data.slug
                        )
                    )
                    if result.scalar_one_or_none():
                        errors.append(
                            f"Item {idx}: Catalog with slug '{catalog_data.slug}' already exists"
                        )
                        logger.warning(
                            f"Skipped creating service catalog with duplicate slug: {catalog_data.slug}"
                        )
                        continue

                    catalog = ServiceCatalog(**catalog_data.model_dump())
                    session.add(catalog)
                    created_catalogs.append(catalog)
                except Exception as e:
                    errors.append(f"Item {idx}: {str(e)}")
                    logger.warning(f"Failed to create catalog at index {idx}: {str(e)}")

            if created_catalogs:
                await session.commit()
                for catalog in created_catalogs:
                    await session.refresh(catalog)

            logger.info(
                f"Created {len(created_catalogs)} service catalog(s), {len(errors)} failed"
            )

            result = [
                ServiceCatalogResponse.model_validate(catalog)
                for catalog in created_catalogs
            ]

            if errors and not created_catalogs:
                raise HTTPException(
                    status_code=400,
                    detail={"message": "All items failed", "errors": errors},
                )

            return result
    except HTTPException:
        raise
    except IntegrityError as e:
        logger.error(f"Integrity error creating service catalogs: {str(e)}")
        raise HTTPException(
            status_code=400, detail="Duplicate slug or integrity constraint violation"
        )
    except DBAPIError as e:
        logger.exception(
            f"Database connection error creating service catalogs: {str(e)}"
        )
        raise DatabaseConnectionError(str(e))
    except SQLAlchemyError as e:
        logger.error(f"Database error creating service catalogs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create service catalogs")
    except Exception as e:
        logger.error(f"Unexpected error creating service catalogs: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def update_service_catalogs(
    catalogs_data: list[ServiceCatalogBulkUpdate],
) -> list[ServiceCatalogResponse]:
    """Update multiple service catalogs in bulk"""
    try:
        async with session_pool() as session:
            catalog_ids = [catalog.id for catalog in catalogs_data]
            result = await session.execute(
                select(ServiceCatalog).where(ServiceCatalog.id.in_(catalog_ids))
            )
            existing_catalogs = {
                catalog.id: catalog for catalog in result.scalars().all()
            }
            missing_ids = set(catalog_ids) - set(existing_catalogs.keys())
            if missing_ids:
                logger.warning(f"Some service catalogs not found: ids={missing_ids}")

            updated_catalogs = []
            errors = []

            for idx, catalog_data in enumerate(catalogs_data):
                catalog_id = catalog_data.id

                if catalog_id not in existing_catalogs:
                    errors.append(f"Item {idx}: Catalog ID {catalog_id} not found")
                    continue

                try:
                    catalog = existing_catalogs[catalog_id]
                    update_data = catalog_data.model_dump(
                        exclude_unset=True, exclude={"id"}
                    )
                    if "slug" in update_data and update_data["slug"] != catalog.slug:
                        result = await session.execute(
                            select(ServiceCatalog).where(
                                ServiceCatalog.slug == update_data["slug"]
                            )
                        )
                        if result.scalar_one_or_none():
                            errors.append(
                                f"Item {idx}: Slug '{update_data['slug']}' already exists"
                            )
                            logger.warning(
                                f"Skipped updating service catalog {catalog_id} - duplicate slug: {update_data['slug']}"
                            )
                            continue
                    for field, value in update_data.items():
                        setattr(catalog, field, value)

                    updated_catalogs.append(catalog)
                except Exception as e:
                    errors.append(f"Item {idx}: {str(e)}")
                    logger.warning(f"Failed to update catalog {catalog_id}: {str(e)}")

            await session.commit()
            for catalog in updated_catalogs:
                await session.refresh(catalog)

            logger.info(f"Updated {len(updated_catalogs)} service catalog(s)")
            return [
                ServiceCatalogResponse.model_validate(catalog)
                for catalog in updated_catalogs
            ]
    except HTTPException:
        raise
    except IntegrityError as e:
        logger.error(f"Integrity error updating service catalogs: {str(e)}")
        raise HTTPException(
            status_code=400, detail="Duplicate slug or integrity constraint violation"
        )
    except DBAPIError as e:
        logger.exception(
            f"Database connection error updating service catalogs: {str(e)}"
        )
        raise DatabaseConnectionError(str(e))
    except SQLAlchemyError as e:
        logger.error(f"Database error updating service catalogs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update service catalogs")
    except Exception as e:
        logger.error(f"Unexpected error updating service catalogs: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def delete_service_catalogs(catalog_ids: list[int]) -> dict:
    """Delete multiple service catalogs"""
    try:
        async with session_pool() as session:
            result = await session.execute(
                select(ServiceCatalog).where(ServiceCatalog.id.in_(catalog_ids))
            )
            catalogs = result.scalars().all()

            missing_ids = set(catalog_ids) - {catalog.id for catalog in catalogs}
            deleted_count = len(catalogs)

            if missing_ids:
                logger.warning(
                    f"Some service catalogs not found for deletion: ids={missing_ids}"
                )

            for catalog in catalogs:
                await session.delete(catalog)

            if deleted_count > 0:
                await session.commit()
                logger.info(f"Deleted {deleted_count} service catalog(s)")

            return {
                "message": f"Deleted {deleted_count} service catalog(s) successfully",
                "deleted_count": deleted_count,
                "missing_ids": list(missing_ids) if missing_ids else [],
            }
    except HTTPException:
        raise
    except IntegrityError as e:
        logger.error(f"Integrity error deleting service catalogs: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail="Cannot delete service catalogs with existing references",
        )
    except DBAPIError as e:
        logger.exception(
            f"Database connection error deleting service catalogs: {str(e)}"
        )
        raise DatabaseConnectionError(str(e))
    except SQLAlchemyError as e:
        logger.error(f"Database error deleting service catalogs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete service catalogs")
    except Exception as e:
        logger.error(f"Unexpected error deleting service catalogs: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
