from pydantic import BaseModel
from typing import Optional


class UserServiceCredentialBase(BaseModel):
    service_id: int
    api_key: Optional[str] = None
    config: Optional[dict] = None
    is_default: bool = False


class UserServiceCredentialCreate(UserServiceCredentialBase):
    pass


class UserServiceCredentialUpdate(BaseModel):
    api_key: Optional[str] = None
    config: Optional[dict] = None
    is_default: Optional[bool] = None


class UserServiceCredentialBulkUpdate(BaseModel):
    id: int
    api_key: Optional[str] = None
    config: Optional[dict] = None
    is_default: Optional[bool] = None


class UserServiceCredentialResponse(UserServiceCredentialBase):
    id: int
    user_id: int
    user_settings_id: int

    class Config:
        from_attributes = True
