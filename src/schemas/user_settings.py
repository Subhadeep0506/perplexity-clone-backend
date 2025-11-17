from pydantic import BaseModel
from typing import Optional


class UserSettingsBase(BaseModel):
    language_preference: Optional[str] = None
    dark_mode_enabled: Optional[bool] = None
    location: Optional[str] = None
    custom_instructions: Optional[str] = None


class UserSettingsCreate(UserSettingsBase):
    pass


class UserSettingsUpdate(UserSettingsBase):
    pass


class UserSettingsResponse(UserSettingsBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
