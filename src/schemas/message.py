from pydantic import BaseModel
from typing import Optional, Any


class MessageBase(BaseModel):
    session_id: int
    user_id: Optional[int] = None
    content: Any
    parent_message_id: Optional[int] = None
    model_used: Optional[str] = None
    confidence_score: Optional[float] = None


class MessageCreate(MessageBase):
    pass


class MessageUpdate(BaseModel):
    content: Optional[Any] = None
    model_used: Optional[str] = None
    confidence_score: Optional[float] = None


class MessageResponse(MessageBase):
    id: int

    class Config:
        from_attributes = True
