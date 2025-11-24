from fastapi import APIRouter, Depends, Body
from ..controllers.user_settings import (
    get_user_settings,
    create_user_settings,
    update_user_settings,
    get_user_service_credentials,
    get_user_service_credential,
    save_user_service_credentials,
    update_user_service_credentials,
    delete_user_service_credentials,
)
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


################################
# User Service Credential Routes
###############################


@router.get("/credentials", response_model=list[UserServiceCredentialResponse])
async def read_user_service_credentials(user_id: int = Depends(get_current_user)):
    """Get all service credentials for current user"""
    return await get_user_service_credentials(user_id)


@router.get(
    "/credentials/{credential_id}", response_model=UserServiceCredentialResponse
)
async def read_user_service_credential(
    credential_id: int, user_id: int = Depends(get_current_user)
):
    """Get a specific service credential"""
    return await get_user_service_credential(user_id, credential_id)


@router.post(
    "/credentials", response_model=list[UserServiceCredentialResponse], status_code=200
)
async def save_user_service_credentials_endpoint(
    credentials_data: list[UserServiceCredentialCreate],
    user_id: int = Depends(get_current_user),
):
    """Save (create or update) multiple service credentials at once"""
    return await save_user_service_credentials(user_id, credentials_data)


@router.put("/credentials", response_model=list[UserServiceCredentialResponse])
async def update_user_service_credentials_endpoint(
    credentials_data: list[UserServiceCredentialBulkUpdate] = Body(...),
    user_id: int = Depends(get_current_user),
):
    """Update multiple service credentials in bulk. Each item should contain 'id' and fields to update."""
    return await update_user_service_credentials(user_id, credentials_data)


@router.delete("/credentials")
async def delete_user_service_credentials_endpoint(
    credential_ids: list[int] = Body(..., embed=True),
    user_id: int = Depends(get_current_user),
):
    """Delete multiple service credentials"""
    return await delete_user_service_credentials(user_id, credential_ids)
