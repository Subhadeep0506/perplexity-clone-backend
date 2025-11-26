"""
Controller for UserAPIKeys management.
Handles CRUD operations for user API keys with encryption.
"""

from sqlalchemy import select, delete
from sqlalchemy.exc import SQLAlchemyError, DBAPIError, IntegrityError
from fastapi import HTTPException
from ..database.database import session_pool, DatabaseConnectionError
from ..models.user_api_keys import UserAPIKeys
from ..models.user_settings import UserSettings
from ..models.user_service_credential import UserServiceCredential
from ..models.service_catalog import ServiceCatalog
from ..schemas.user_api_keys import (
    UserAPIKeyCreate,
    UserAPIKeyUpdate,
    UserAPIKeyResponse,
    UserAPIKeyWithServices,
    UserAPIKeyListResponse,
)
from ..utils.encryption import encrypt_api_key, decrypt_api_key, mask_api_key
from ..services.logger import SingletonLogger

logger = SingletonLogger().get_logger()


async def get_user_api_keys(user_id: int) -> UserAPIKeyListResponse:
    """
    Get all API keys for a user with masked keys and associated service IDs.

    Args:
        user_id: User ID

    Returns:
        UserAPIKeyListResponse with masked keys
    """
    try:
        async with session_pool() as session:
            # Get user settings
            settings_result = await session.execute(
                select(UserSettings).where(UserSettings.user_id == user_id)
            )
            settings = settings_result.scalar_one_or_none()
            if not settings:
                logger.warning(f"User settings not found for user_id={user_id}")
                return UserAPIKeyListResponse(api_keys=[])

            # Get all API keys for the user
            result = await session.execute(
                select(UserAPIKeys).where(UserAPIKeys.user_id == user_id)
            )
            api_keys = result.scalars().all()

            # Build response with masked keys and service IDs
            responses = []
            for api_key in api_keys:
                # Get associated service credentials
                creds_result = await session.execute(
                    select(UserServiceCredential.service_id).where(
                        UserServiceCredential.api_key_id == api_key.id
                    )
                )
                service_ids = [row[0] for row in creds_result.all()]

                # Decrypt and mask the API key for display
                try:
                    decrypted_key = decrypt_api_key(api_key.encrypted_api_key)
                    masked_key_value = mask_api_key(decrypted_key)
                except Exception as e:
                    logger.error(f"Failed to decrypt API key id={api_key.id}: {str(e)}")
                    masked_key_value = "***"

                response = UserAPIKeyResponse(
                    id=api_key.id,
                    user_id=api_key.user_id,
                    user_settings_id=api_key.user_settings_id,
                    title=api_key.title,
                    is_active=api_key.is_active,
                    masked_key=masked_key_value,
                    service_ids=service_ids,
                    created_at=api_key.created_at,
                    updated_at=api_key.updated_at,
                )
                responses.append(response)

            return UserAPIKeyListResponse(api_keys=responses)

    except DBAPIError as e:
        logger.exception(
            f"Database connection error fetching API keys for user_id={user_id}: {str(e)}"
        )
        raise DatabaseConnectionError(str(e))
    except SQLAlchemyError as e:
        logger.error(
            f"Database error fetching API keys for user_id={user_id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Failed to retrieve API keys")
    except Exception as e:
        logger.error(
            f"Unexpected error fetching API keys for user_id={user_id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Internal server error")


async def get_user_api_key(user_id: int, api_key_id: int) -> UserAPIKeyWithServices:
    """
    Get a specific API key with full service details.

    Args:
        user_id: User ID
        api_key_id: API key ID

    Returns:
        UserAPIKeyWithServices with full service details
    """
    try:
        async with session_pool() as session:
            # Get the API key
            result = await session.execute(
                select(UserAPIKeys).where(
                    UserAPIKeys.id == api_key_id,
                    UserAPIKeys.user_id == user_id,
                )
            )
            api_key = result.scalar_one_or_none()
            if not api_key:
                logger.warning(
                    f"API key id={api_key_id} not found for user_id={user_id}"
                )
                raise HTTPException(status_code=404, detail="API key not found")

            # Get associated service credentials with service details
            creds_result = await session.execute(
                select(UserServiceCredential, ServiceCatalog)
                .join(
                    ServiceCatalog,
                    UserServiceCredential.service_id == ServiceCatalog.id,
                )
                .where(UserServiceCredential.api_key_id == api_key.id)
            )
            creds_with_services = creds_result.all()

            service_ids = []
            services = []
            for cred, service in creds_with_services:
                service_ids.append(cred.service_id)
                services.append(
                    {
                        "id": service.id,
                        "name": service.name,
                        "slug": service.slug,
                        "category": service.category,
                        "provider": service.provider,
                        "is_active": service.is_active,
                    }
                )

            # Decrypt and mask the API key
            try:
                decrypted_key = decrypt_api_key(api_key.encrypted_api_key)
                masked_key_value = mask_api_key(decrypted_key)
            except Exception as e:
                logger.error(f"Failed to decrypt API key id={api_key.id}: {str(e)}")
                masked_key_value = "***"

            return UserAPIKeyWithServices(
                id=api_key.id,
                user_id=api_key.user_id,
                user_settings_id=api_key.user_settings_id,
                title=api_key.title,
                is_active=api_key.is_active,
                masked_key=masked_key_value,
                service_ids=service_ids,
                services=services,
                created_at=api_key.created_at,
                updated_at=api_key.updated_at,
            )

    except HTTPException:
        raise
    except DBAPIError as e:
        logger.exception(
            f"Database connection error fetching API key id={api_key_id}: {str(e)}"
        )
        raise DatabaseConnectionError(str(e))
    except SQLAlchemyError as e:
        logger.error(f"Database error fetching API key id={api_key_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve API key")
    except Exception as e:
        logger.error(f"Unexpected error fetching API key id={api_key_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def create_user_api_key(
    user_id: int, api_key_data: UserAPIKeyCreate
) -> UserAPIKeyResponse:
    """
    Create a new API key and associate it with services.

    Args:
        user_id: User ID
        api_key_data: API key creation data with plain text key and service IDs

    Returns:
        Created UserAPIKeyResponse
    """
    try:
        async with session_pool() as session:
            # Get or create user settings
            settings_result = await session.execute(
                select(UserSettings).where(UserSettings.user_id == user_id)
            )
            settings = settings_result.scalar_one_or_none()
            if not settings:
                settings = UserSettings(user_id=user_id)
                session.add(settings)
                await session.flush()

            # Validate that all service IDs exist and are active
            services_result = await session.execute(
                select(ServiceCatalog).where(
                    ServiceCatalog.id.in_(api_key_data.service_ids),
                    ServiceCatalog.is_active == True,
                )
            )
            services = services_result.scalars().all()
            if len(services) != len(api_key_data.service_ids):
                invalid_ids = set(api_key_data.service_ids) - {s.id for s in services}
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid or inactive service IDs: {invalid_ids}",
                )

            # Encrypt the API key
            encrypted_key = encrypt_api_key(api_key_data.api_key)

            # Create the API key record
            new_api_key = UserAPIKeys(
                user_id=user_id,
                user_settings_id=settings.id,
                title=api_key_data.title,
                encrypted_api_key=encrypted_key,
                is_active=True,
            )
            session.add(new_api_key)
            await session.flush()

            # Create service credentials for each service
            for service_id in api_key_data.service_ids:
                credential = UserServiceCredential(
                    user_id=user_id,
                    user_settings_id=settings.id,
                    service_id=service_id,
                    api_key_id=new_api_key.id,
                    is_default=False,
                )
                session.add(credential)

            await session.commit()
            await session.refresh(new_api_key)

            # Build response with masked key
            masked_key_value = mask_api_key(api_key_data.api_key)

            return UserAPIKeyResponse(
                id=new_api_key.id,
                user_id=new_api_key.user_id,
                user_settings_id=new_api_key.user_settings_id,
                title=new_api_key.title,
                is_active=new_api_key.is_active,
                masked_key=masked_key_value,
                service_ids=api_key_data.service_ids,
                created_at=new_api_key.created_at,
                updated_at=new_api_key.updated_at,
            )

    except HTTPException:
        raise
    except IntegrityError as e:
        logger.error(
            f"Integrity error creating API key for user_id={user_id}: {str(e)}"
        )
        await session.rollback()
        raise HTTPException(
            status_code=400, detail="Failed to create API key due to data constraint"
        )
    except DBAPIError as e:
        logger.exception(
            f"Database connection error creating API key for user_id={user_id}: {str(e)}"
        )
        raise DatabaseConnectionError(str(e))
    except SQLAlchemyError as e:
        logger.error(f"Database error creating API key for user_id={user_id}: {str(e)}")
        await session.rollback()
        raise HTTPException(status_code=500, detail="Failed to create API key")
    except Exception as e:
        logger.error(
            f"Unexpected error creating API key for user_id={user_id}: {str(e)}"
        )
        await session.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


async def update_user_api_key(
    user_id: int, api_key_id: int, api_key_data: UserAPIKeyUpdate
) -> UserAPIKeyResponse:
    """
    Update an existing API key.
    Can update title, API key value, active status, and associated services.

    Args:
        user_id: User ID
        api_key_id: API key ID to update
        api_key_data: Updated data

    Returns:
        Updated UserAPIKeyResponse
    """
    try:
        async with session_pool() as session:
            # Get the API key
            result = await session.execute(
                select(UserAPIKeys).where(
                    UserAPIKeys.id == api_key_id,
                    UserAPIKeys.user_id == user_id,
                )
            )
            api_key = result.scalar_one_or_none()
            if not api_key:
                logger.warning(
                    f"API key id={api_key_id} not found for user_id={user_id}"
                )
                raise HTTPException(status_code=404, detail="API key not found")

            # Update fields
            update_data = api_key_data.model_dump(
                exclude_unset=True, exclude={"service_ids", "api_key"}
            )
            for field, value in update_data.items():
                setattr(api_key, field, value)

            # Update encrypted API key if provided
            if api_key_data.api_key:
                api_key.encrypted_api_key = encrypt_api_key(api_key_data.api_key)

            # Update service associations if provided
            current_service_ids = []
            if api_key_data.service_ids is not None:
                # Validate service IDs
                services_result = await session.execute(
                    select(ServiceCatalog).where(
                        ServiceCatalog.id.in_(api_key_data.service_ids),
                        ServiceCatalog.is_active == True,
                    )
                )
                services = services_result.scalars().all()
                if len(services) != len(api_key_data.service_ids):
                    invalid_ids = set(api_key_data.service_ids) - {
                        s.id for s in services
                    }
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid or inactive service IDs: {invalid_ids}",
                    )

                # Delete existing service credentials
                await session.execute(
                    delete(UserServiceCredential).where(
                        UserServiceCredential.api_key_id == api_key_id
                    )
                )

                # Create new service credentials
                for service_id in api_key_data.service_ids:
                    credential = UserServiceCredential(
                        user_id=user_id,
                        user_settings_id=api_key.user_settings_id,
                        service_id=service_id,
                        api_key_id=api_key.id,
                        is_default=False,
                    )
                    session.add(credential)

                current_service_ids = api_key_data.service_ids
            else:
                # Get current service IDs
                creds_result = await session.execute(
                    select(UserServiceCredential.service_id).where(
                        UserServiceCredential.api_key_id == api_key.id
                    )
                )
                current_service_ids = [row[0] for row in creds_result.all()]

            await session.commit()
            await session.refresh(api_key)

            # Build response with masked key
            try:
                decrypted_key = decrypt_api_key(api_key.encrypted_api_key)
                masked_key_value = mask_api_key(decrypted_key)
            except Exception as e:
                logger.error(f"Failed to decrypt API key id={api_key.id}: {str(e)}")
                masked_key_value = "***"

            return UserAPIKeyResponse(
                id=api_key.id,
                user_id=api_key.user_id,
                user_settings_id=api_key.user_settings_id,
                title=api_key.title,
                is_active=api_key.is_active,
                masked_key=masked_key_value,
                service_ids=current_service_ids,
                created_at=api_key.created_at,
                updated_at=api_key.updated_at,
            )

    except HTTPException:
        raise
    except DBAPIError as e:
        logger.exception(
            f"Database connection error updating API key id={api_key_id}: {str(e)}"
        )
        raise DatabaseConnectionError(str(e))
    except SQLAlchemyError as e:
        logger.error(f"Database error updating API key id={api_key_id}: {str(e)}")
        await session.rollback()
        raise HTTPException(status_code=500, detail="Failed to update API key")
    except Exception as e:
        logger.error(f"Unexpected error updating API key id={api_key_id}: {str(e)}")
        await session.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


async def delete_user_api_key(user_id: int, api_key_id: int) -> dict:
    """
    Delete an API key and all associated service credentials.

    Args:
        user_id: User ID
        api_key_id: API key ID to delete

    Returns:
        Success message
    """
    try:
        async with session_pool() as session:
            # Get the API key
            result = await session.execute(
                select(UserAPIKeys).where(
                    UserAPIKeys.id == api_key_id,
                    UserAPIKeys.user_id == user_id,
                )
            )
            api_key = result.scalar_one_or_none()
            if not api_key:
                logger.warning(
                    f"API key id={api_key_id} not found for user_id={user_id}"
                )
                raise HTTPException(status_code=404, detail="API key not found")

            # Delete the API key (cascades to service credentials)
            await session.delete(api_key)
            await session.commit()

            logger.info(f"Deleted API key id={api_key_id} for user_id={user_id}")
            return {"message": "API key deleted successfully"}

    except HTTPException:
        raise
    except DBAPIError as e:
        logger.exception(
            f"Database connection error deleting API key id={api_key_id}: {str(e)}"
        )
        raise DatabaseConnectionError(str(e))
    except SQLAlchemyError as e:
        logger.error(f"Database error deleting API key id={api_key_id}: {str(e)}")
        await session.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete API key")
    except Exception as e:
        logger.error(f"Unexpected error deleting API key id={api_key_id}: {str(e)}")
        await session.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")
