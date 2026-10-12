import datetime
from pydantic import BaseModel
from typing import Optional, List

class SessionCreate(BaseModel):
    title: Optional[str] = "New Conversation"
    provider: Optional[str] = "local"
    model_name: Optional[str] = None

class SessionResponse(BaseModel):
    id: str
    title: str
    provider: str
    model_name: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    message_count: Optional[int] = 0

    class Config:
        from_attributes = True

class SessionDetailResponse(BaseModel):
    id: str
    title: str
    provider: str
    model_name: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    messages: List["MessageResponse"] = []

    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    skill: Optional[str] = None
    citations: Optional[List[dict]] = []
    created_at: datetime.datetime

    class Config:
        from_attributes = True

SessionDetailResponse.model_rebuild()
