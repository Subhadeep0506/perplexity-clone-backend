from fastapi import APIRouter, Depends
from ..controllers.user_settings import (
    get_user_settings,
    create_user_settings,
    update_user_settings,
)
from ..schemas.user_settings import (
    UserSettingsCreate,
    UserSettingsUpdate,
    UserSettingsResponse,
)
from ..lib.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=UserSettingsResponse)
async def read_user_settings(user_id: int = Depends(get_current_user)):
    """Get current user's settings"""
    return await get_user_settings(user_id)


@router.post("/", response_model=UserSettingsResponse)
async def create_user_settings_endpoint(
    settings_data: UserSettingsCreate, user_id: int = Depends(get_current_user)
):
    """Create user settings"""
    return await create_user_settings(user_id, settings_data)


@router.put("/", response_model=UserSettingsResponse)
async def update_user_settings_endpoint(
    settings_data: UserSettingsUpdate, user_id: int = Depends(get_current_user)
):
    """Update user settings"""
    return await update_user_settings(user_id, settings_data)
