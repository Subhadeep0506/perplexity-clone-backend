from sqlalchemy import select
from fastapi import HTTPException
from ..database.database import session_pool
from ..models.user_settings import UserSettings
from ..models.user import User
from ..schemas.user_settings import (
    UserSettingsCreate,
    UserSettingsUpdate,
    UserSettingsResponse,
)


async def get_user_settings(user_id: int) -> UserSettingsResponse:
    """Get user settings"""
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


async def create_user_settings(
    user_id: int, settings_data: UserSettingsCreate
) -> UserSettingsResponse:
    """Create user settings"""
    async with session_pool() as session:
        # Check if settings already exist
        result = await session.execute(
            select(UserSettings).where(UserSettings.user_id == user_id)
        )
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="User settings already exist")

        settings = UserSettings(user_id=user_id, **settings_data.model_dump())
        session.add(settings)
        await session.commit()
        await session.refresh(settings)
        return UserSettingsResponse.model_validate(settings)


async def update_user_settings(
    user_id: int, settings_data: UserSettingsUpdate
) -> UserSettingsResponse:
    """Update user settings"""
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
