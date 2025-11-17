from sqlalchemy import select
from fastapi import HTTPException, UploadFile
from ..database.database import session_pool
from ..models.profile import Profile
from ..models.user import User
from ..schemas.profile import ProfileCreate, ProfileUpdate, ProfileResponse
from ..lib.storage import storage


async def get_profile(user_id: int) -> ProfileResponse:
    """Get user profile"""
    async with session_pool() as session:
        result = await session.execute(
            select(Profile).where(Profile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        # Convert to dict and add avatar_url
        profile_dict = {
            "id": profile.id,
            "user_id": profile.user_id,
            "phone": profile.phone,
            "bio": profile.bio,
            "avatar_url": (
                storage.get_file_url(profile.avatar) if profile.avatar else None
            ),
        }
        return ProfileResponse(**profile_dict)


async def create_profile(user_id: int, profile_data: ProfileCreate) -> ProfileResponse:
    """Create user profile"""
    async with session_pool() as session:
        # Check if profile already exists
        result = await session.execute(
            select(Profile).where(Profile.user_id == user_id)
        )
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Profile already exists")

        profile = Profile(user_id=user_id, **profile_data.model_dump())
        session.add(profile)
        await session.commit()
        await session.refresh(profile)

        # Return with avatar URL
        profile_dict = {
            "id": profile.id,
            "user_id": profile.user_id,
            "phone": profile.phone,
            "bio": profile.bio,
            "avatar_url": (
                storage.get_file_url(profile.avatar) if profile.avatar else None
            ),
        }
        return ProfileResponse(**profile_dict)


async def update_profile(user_id: int, profile_data: ProfileUpdate) -> ProfileResponse:
    """Update user profile"""
    async with session_pool() as session:
        result = await session.execute(
            select(Profile).where(Profile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        update_data = profile_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(profile, field, value)

        await session.commit()
        await session.refresh(profile)

        # Return with avatar URL
        profile_dict = {
            "id": profile.id,
            "user_id": profile.user_id,
            "phone": profile.phone,
            "bio": profile.bio,
            "avatar_url": (
                storage.get_file_url(profile.avatar) if profile.avatar else None
            ),
        }
        return ProfileResponse(**profile_dict)


async def upload_avatar(user_id: int, file: UploadFile) -> ProfileResponse:
    """Upload avatar for user profile"""
    async with session_pool() as session:
        result = await session.execute(
            select(Profile).where(Profile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        # Delete old avatar if exists
        if profile.avatar:
            await storage.delete_file(profile.avatar)

        # Upload new avatar
        avatar_key = await storage.upload_file(file, user_id, "avatar")

        # Update profile
        profile.avatar = avatar_key
        await session.commit()
        await session.refresh(profile)

        # Return with avatar URL
        profile_dict = {
            "id": profile.id,
            "user_id": profile.user_id,
            "phone": profile.phone,
            "bio": profile.bio,
            "avatar_url": (
                storage.get_file_url(profile.avatar) if profile.avatar else None
            ),
        }
        return ProfileResponse(**profile_dict)
