from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError, DBAPIError
from fastapi import HTTPException
from ..database.database import session_pool, DatabaseConnectionError
from ..models.user_settings import UserSettings
from ..models.user import User
from ..models.user_service_credential import UserServiceCredential
from ..schemas.user_settings import (
    UserSettingsCreate,
    UserSettingsUpdate,
    UserSettingsResponse,
)
from ..schemas.user_service_credential import (
    UserServiceCredentialCreate,
    UserServiceCredentialUpdate,
    UserServiceCredentialBulkUpdate,
    UserServiceCredentialResponse,
    UserServiceCredentialListResponse,
)
from ..services.logger import SingletonLogger

logger = SingletonLogger().get_logger()


async def get_user_settings(user_id: int) -> UserSettingsResponse:
    """Get user settings"""
    try:
        async with session_pool() as session:
            result = await session.execute(
                select(UserSettings).where(UserSettings.user_id == user_id)
            )
            settings = result.scalar_one_or_none()
            if not settings:
                # Create default settings if not exist
                settings = UserSettings(user_id=user_id)
                session.add(settings)
                await session.commit()
                await session.refresh(settings)
            return UserSettingsResponse.model_validate(settings)
    except DBAPIError as e:
        logger.exception(
            f"Database connection error fetching settings for user_id={user_id}: {str(e)}"
        )
        raise DatabaseConnectionError(str(e))
    except SQLAlchemyError as e:
        logger.error(
            f"Database error fetching settings for user_id={user_id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Failed to retrieve user settings")
    except Exception as e:
        logger.error(
            f"Unexpected error fetching settings for user_id={user_id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Internal server error")


async def create_user_settings(
    user_id: int, settings_data: UserSettingsCreate
) -> UserSettingsResponse:
    """Create user settings"""
    try:
        async with session_pool() as session:
            # Check if settings already exist
            result = await session.execute(
                select(UserSettings).where(UserSettings.user_id == user_id)
            )
            if result.scalar_one_or_none():
                logger.warning(
                    f"Attempted to create duplicate settings for user_id={user_id}"
                )
                raise HTTPException(
                    status_code=400, detail="User settings already exist"
                )

            settings = UserSettings(user_id=user_id, **settings_data.model_dump())
            session.add(settings)
            await session.commit()
            await session.refresh(settings)
            return UserSettingsResponse.model_validate(settings)
    except HTTPException:
        raise
    except DBAPIError as e:
        logger.exception(
            f"Database connection error creating settings for user_id={user_id}: {str(e)}"
        )
        raise DatabaseConnectionError(str(e))
    except SQLAlchemyError as e:
        logger.error(
            f"Database error creating settings for user_id={user_id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Failed to create user settings")
    except Exception as e:
        logger.error(
            f"Unexpected error creating settings for user_id={user_id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Internal server error")


async def update_user_settings(
    user_id: int, settings_data: UserSettingsUpdate
) -> UserSettingsResponse:
    """Update user settings"""
    try:
        async with session_pool() as session:
            result = await session.execute(
                select(UserSettings).where(UserSettings.user_id == user_id)
            )
            settings = result.scalar_one_or_none()
            if not settings:
                # Create with defaults and update
                settings = UserSettings(user_id=user_id)
                session.add(settings)

            update_data = settings_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(settings, field, value)

            await session.commit()
            await session.refresh(settings)
            return UserSettingsResponse.model_validate(settings)
    except DBAPIError as e:
        logger.exception(
            f"Database connection error updating settings for user_id={user_id}: {str(e)}"
        )
        raise DatabaseConnectionError(str(e))
    except SQLAlchemyError as e:
        logger.error(
            f"Database error updating settings for user_id={user_id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Failed to update user settings")
    except Exception as e:
        logger.error(
            f"Unexpected error updating settings for user_id={user_id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Internal server error")


# User Service Credential CRUD operations


async def get_user_service_credentials(
    user_id: int,
) -> UserServiceCredentialListResponse:
    """Get all service credentials for a user"""
    try:
        async with session_pool() as session:
            # Get user settings first
            settings_result = await session.execute(
                select(UserSettings).where(UserSettings.user_id == user_id)
            )
            settings = settings_result.scalar_one_or_none()
            if not settings:
                return UserServiceCredentialListResponse(credentials=[])

            result = await session.execute(
                select(UserServiceCredential).where(
                    UserServiceCredential.user_id == user_id
                )
            )
            credentials = result.scalars().all()
            cred_list = [
                UserServiceCredentialResponse.model_validate(cred)
                for cred in credentials
            ]
            return UserServiceCredentialListResponse(credentials=cred_list)
    except DBAPIError as e:
        logger.exception(
            f"Database connection error fetching credentials for user_id={user_id}: {str(e)}"
        )
        raise DatabaseConnectionError(str(e))
    except SQLAlchemyError as e:
        logger.error(
            f"Database error fetching credentials for user_id={user_id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Failed to retrieve credentials")
    except Exception as e:
        logger.error(
            f"Unexpected error fetching credentials for user_id={user_id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Internal server error")


async def get_user_service_credential(
    user_id: int, credential_id: int
) -> UserServiceCredentialResponse:
    """Get a specific service credential"""
    try:
        async with session_pool() as session:
            result = await session.execute(
                select(UserServiceCredential).where(
                    UserServiceCredential.id == credential_id,
                    UserServiceCredential.user_id == user_id,
                )
            )
            credential = result.scalar_one_or_none()
            if not credential:
                logger.warning(
                    f"Credential_id={credential_id} not found for user_id={user_id}"
                )
                raise HTTPException(status_code=404, detail="Credential not found")
            return UserServiceCredentialResponse.model_validate(credential)
    except HTTPException:
        raise
    except DBAPIError as e:
        logger.exception(
            f"Database connection error fetching credential_id={credential_id} for user_id={user_id}: {str(e)}"
        )
        raise DatabaseConnectionError(str(e))
    except SQLAlchemyError as e:
        logger.error(
            f"Database error fetching credential_id={credential_id} for user_id={user_id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Failed to retrieve credential")
    except Exception as e:
        logger.error(
            f"Unexpected error fetching credential_id={credential_id} for user_id={user_id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Internal server error")


async def save_user_service_credentials(
    user_id: int, credentials_data: list[UserServiceCredentialCreate]
) -> list[UserServiceCredentialResponse]:
    """
    Create or update multiple service credentials at once.
    Note: This function expects api_key_id to be provided in credentials_data.
    Use the user_api_keys controller to create API keys first.
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

            # Validate that the API keys exist and belong to the user
            from ..models.user_api_keys import UserAPIKeys

            api_key_ids = {cred.api_key_id for cred in credentials_data}
            api_keys_result = await session.execute(
                select(UserAPIKeys).where(
                    UserAPIKeys.id.in_(api_key_ids),
                    UserAPIKeys.user_id == user_id,
                    UserAPIKeys.is_active == True,
                )
            )
            valid_api_keys = {key.id for key in api_keys_result.scalars().all()}
            invalid_api_key_ids = api_key_ids - valid_api_keys
            if invalid_api_key_ids:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid or inactive API key IDs: {invalid_api_key_ids}",
                )

            # Get all existing credentials for this user
            existing_result = await session.execute(
                select(UserServiceCredential).where(
                    UserServiceCredential.user_id == user_id
                )
            )
            existing_credentials = {
                (cred.service_id, cred.api_key_id): cred
                for cred in existing_result.scalars().all()
            }

            saved_credentials = []
            for cred_data in credentials_data:
                key = (cred_data.service_id, cred_data.api_key_id)
                if key in existing_credentials:
                    # Update existing
                    credential = existing_credentials[key]
                    for field, value in cred_data.model_dump(
                        exclude_unset=True
                    ).items():
                        if field not in [
                            "service_id",
                            "api_key_id",
                        ]:  # Don't update keys
                            setattr(credential, field, value)
                else:
                    # Create new
                    credential = UserServiceCredential(
                        user_id=user_id,
                        user_settings_id=settings.id,
                        **cred_data.model_dump(),
                    )
                    session.add(credential)
                saved_credentials.append(credential)

            await session.commit()
            for cred in saved_credentials:
                await session.refresh(cred)

            return [
                UserServiceCredentialResponse.model_validate(cred)
                for cred in saved_credentials
            ]
    except HTTPException:
        raise
    except DBAPIError as e:
        logger.exception(
            f"Database connection error saving credentials for user_id={user_id}: {str(e)}"
        )
        raise DatabaseConnectionError(str(e))
    except SQLAlchemyError as e:
        logger.error(
            f"Database error saving credentials for user_id={user_id}: {str(e)}"
        )
        await session.rollback()
        raise HTTPException(status_code=500, detail="Failed to save credentials")
    except Exception as e:
        logger.error(
            f"Unexpected error saving credentials for user_id={user_id}: {str(e)}"
        )
        await session.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


async def update_user_service_credentials(
    user_id: int, credentials_data: list[UserServiceCredentialBulkUpdate]
) -> list[UserServiceCredentialResponse]:
    """Update multiple service credentials in bulk"""
    try:
        async with session_pool() as session:
            # Extract credential IDs from the input
            credential_ids = [cred.id for cred in credentials_data]

            # Fetch existing credentials
            result = await session.execute(
                select(UserServiceCredential).where(
                    UserServiceCredential.id.in_(credential_ids),
                    UserServiceCredential.user_id == user_id,
                )
            )
            existing_credentials = {cred.id: cred for cred in result.scalars().all()}

            # Process each credential individually
            missing_ids = set(credential_ids) - set(existing_credentials.keys())
            if missing_ids:
                logger.warning(
                    f"Some credentials not found for user_id={user_id}: ids={missing_ids}"
                )

            updated_credentials = []
            errors = []

            for idx, cred_data in enumerate(credentials_data):
                credential_id = cred_data.id

                if credential_id not in existing_credentials:
                    errors.append(
                        f"Item {idx}: Credential ID {credential_id} not found"
                    )
                    continue

                try:
                    credential = existing_credentials[credential_id]

                    # Update only the provided fields using model_dump(exclude_unset=True)
                    update_data = cred_data.model_dump(
                        exclude_unset=True, exclude={"id"}
                    )
                    for field, value in update_data.items():
                        setattr(credential, field, value)

                    updated_credentials.append(credential)
                except Exception as e:
                    errors.append(f"Item {idx}: {str(e)}")
                    logger.warning(
                        f"Failed to update credential {credential_id}: {str(e)}"
                    )

            await session.commit()
            for cred in updated_credentials:
                await session.refresh(cred)

            return [
                UserServiceCredentialResponse.model_validate(cred)
                for cred in updated_credentials
            ]
    except HTTPException:
        raise
    except DBAPIError as e:
        logger.exception(
            f"Database connection error updating credentials for user_id={user_id}: {str(e)}"
        )
        raise DatabaseConnectionError(str(e))
    except SQLAlchemyError as e:
        logger.error(
            f"Database error updating credentials for user_id={user_id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Failed to update credentials")
    except Exception as e:
        logger.error(
            f"Unexpected error updating credentials for user_id={user_id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Internal server error")


async def delete_user_service_credentials(
    user_id: int, credential_ids: list[int]
) -> dict:
    """Delete multiple service credentials"""
    try:
        async with session_pool() as session:
            result = await session.execute(
                select(UserServiceCredential).where(
                    UserServiceCredential.id.in_(credential_ids),
                    UserServiceCredential.user_id == user_id,
                )
            )
            credentials = result.scalars().all()

            missing_ids = set(credential_ids) - {cred.id for cred in credentials}
            deleted_count = len(credentials)

            if missing_ids:
                logger.warning(
                    f"Some credentials not found for user_id={user_id}: ids={missing_ids}"
                )

            for credential in credentials:
                await session.delete(credential)

            if deleted_count > 0:
                await session.commit()
                logger.info(
                    f"Deleted {deleted_count} credential(s) for user_id={user_id}"
                )

            return {
                "message": f"Deleted {deleted_count} credential(s) successfully",
                "deleted_count": deleted_count,
                "missing_ids": list(missing_ids) if missing_ids else [],
            }
    except HTTPException:
        raise
    except DBAPIError as e:
        logger.exception(
            f"Database connection error deleting credentials for user_id={user_id}: {str(e)}"
        )
        raise DatabaseConnectionError(str(e))
    except SQLAlchemyError as e:
        logger.error(
            f"Database error deleting credentials for user_id={user_id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Failed to delete credentials")
    except Exception as e:
        logger.error(
            f"Unexpected error deleting credentials for user_id={user_id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Internal server error")
