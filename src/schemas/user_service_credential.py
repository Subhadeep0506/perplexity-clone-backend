from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserServiceCredentialBase(BaseModel):
    """Base schema for UserServiceCredential"""

    service_id: int = Field(..., description="Service catalog ID")
    api_key_id: int = Field(..., description="User API key ID to use for this service")
    config: Optional[dict] = Field(None, description="Service-specific configuration")
    is_default: bool = Field(
        False, description="Whether this is the default credential for the service"
    )


class UserServiceCredentialCreate(UserServiceCredentialBase):
    """Schema for creating a service credential (used internally)"""

    pass


class UserServiceCredentialUpdate(BaseModel):
    """Schema for updating a service credential"""

    api_key_id: Optional[int] = Field(
        None, description="Change the API key used for this service"
    )
    config: Optional[dict] = None
    is_default: Optional[bool] = None


class UserServiceCredentialBulkUpdate(BaseModel):
    """Schema for bulk updating service credentials"""

    id: int
    api_key_id: Optional[int] = None
    config: Optional[dict] = None
    is_default: Optional[bool] = None


class UserServiceCredentialResponse(BaseModel):
    """Schema for service credential response"""

    id: int
    user_id: int
    user_settings_id: int
    service_id: int
    api_key_id: int
    config: Optional[dict] = None
    is_default: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserServiceCredentialWithDetails(UserServiceCredentialResponse):
    """Schema with service and API key details"""

    service_name: Optional[str] = None
    service_provider: Optional[str] = None
    api_key_title: Optional[str] = None

    class Config:
        from_attributes = True


class UserServiceCredentialListResponse(BaseModel):
    """Schema for list of service credentials response"""

    credentials: list[UserServiceCredentialResponse]

    class Config:
        from_attributes = True
