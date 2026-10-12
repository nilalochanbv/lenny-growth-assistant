import datetime
from pydantic import BaseModel
from typing import Optional

class ArtifactResponse(BaseModel):
    id: str
    session_id: str
    title: str
    format: str  # "markdown" or "html"
    content: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True

class ArtifactCreate(BaseModel):
    session_id: str
    title: str
    format: str
    content: str
