"""
Pydantic schemas for UserAPIKeys management.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserAPIKeyBase(BaseModel):
    """Base schema for UserAPIKey"""

    title: str = Field(
        ...,
        min_length=1,
        max_length=512,
        description="Descriptive title for the API key",
    )


class UserAPIKeyCreate(UserAPIKeyBase):
    """Schema for creating a new API key"""

    api_key: str = Field(
        ..., min_length=1, description="Plain text API key (will be encrypted)"
    )
    service_ids: list[int] = Field(
        ...,
        min_items=1,
        description="List of service IDs to associate with this API key",
    )


class UserAPIKeyUpdate(BaseModel):
    """Schema for updating an existing API key"""

    title: Optional[str] = Field(None, min_length=1, max_length=512)
    api_key: Optional[str] = Field(
        None, min_length=1, description="New plain text API key (will be encrypted)"
    )
    is_active: Optional[bool] = None
    service_ids: Optional[list[int]] = Field(
        None, min_items=1, description="Updated list of service IDs"
    )


class UserAPIKeyResponse(UserAPIKeyBase):
    """Schema for API key response (without exposing the actual key)"""

    id: int
    user_id: int
    user_settings_id: int
    is_active: bool
    masked_key: Optional[str] = Field(
        None, description="Masked version of the API key for display"
    )
    service_ids: list[int] = Field(
        default_factory=list, description="List of associated service IDs"
    )
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserAPIKeyWithServices(UserAPIKeyResponse):
    """Schema for API key with full service details"""

    services: list[dict] = Field(
        default_factory=list, description="Full service details from service catalog"
    )

    class Config:
        from_attributes = True


class UserAPIKeyListResponse(BaseModel):
    """Schema for list of API keys response"""

    api_keys: list[UserAPIKeyResponse]

    class Config:
        from_attributes = True
