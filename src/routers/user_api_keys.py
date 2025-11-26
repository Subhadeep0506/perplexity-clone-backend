"""
Router for UserAPIKeys management.
Provides endpoints for managing user API keys and their service associations.
"""

from fastapi import APIRouter, Depends, HTTPException
from ..controllers.user_api_keys import (
    get_user_api_keys,
    get_user_api_key,
    create_user_api_key,
    update_user_api_key,
    delete_user_api_key,
)
from ..schemas.user_api_keys import (
    UserAPIKeyCreate,
    UserAPIKeyUpdate,
    UserAPIKeyResponse,
    UserAPIKeyWithServices,
    UserAPIKeyListResponse,
)
from ..lib.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=UserAPIKeyListResponse)
async def read_user_api_keys(user_id: int = Depends(get_current_user)):
    """
    Get all API keys for the current user.
    Returns masked API keys with associated service IDs.
    """
    return await get_user_api_keys(user_id)


@router.get("/{api_key_id}", response_model=UserAPIKeyWithServices)
async def read_user_api_key(api_key_id: int, user_id: int = Depends(get_current_user)):
    """
    Get a specific API key with full service details.
    Returns masked API key with complete service information.
    """
    return await get_user_api_key(user_id, api_key_id)


@router.post("/", response_model=UserAPIKeyResponse, status_code=201)
async def create_api_key(
    api_key_data: UserAPIKeyCreate, user_id: int = Depends(get_current_user)
):
    """
    Create a new API key and associate it with services.

    The API key will be encrypted before storage.
    Automatically creates service credentials for each service ID provided.

    Request body:
    - title: Descriptive name for the API key
    - api_key: Plain text API key (will be encrypted)
    - service_ids: List of service IDs to associate with this key
    """
    return await create_user_api_key(user_id, api_key_data)


@router.put("/{api_key_id}", response_model=UserAPIKeyResponse)
async def update_api_key(
    api_key_id: int,
    api_key_data: UserAPIKeyUpdate,
    user_id: int = Depends(get_current_user),
):
    """
    Update an existing API key.

    Can update:
    - title: Change the descriptive name
    - api_key: Update the API key value (will be re-encrypted)
    - is_active: Activate/deactivate the key
    - service_ids: Update associated services (recreates service credentials)

    All fields are optional.
    """
    return await update_user_api_key(user_id, api_key_id, api_key_data)


@router.delete("/{api_key_id}")
async def delete_api_key(api_key_id: int, user_id: int = Depends(get_current_user)):
    """
    Delete an API key and all associated service credentials.

    This operation cascades to delete all service credentials using this API key.
    """
    return await delete_user_api_key(user_id, api_key_id)
