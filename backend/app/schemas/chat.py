import datetime
from pydantic import BaseModel
from typing import Optional, List
from backend.app.schemas.rag import Citation
from backend.app.schemas.artifact import ArtifactResponse

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    provider: Optional[str] = None  # "local" or "cloud"
    model_name: Optional[str] = None
    skill: Optional[str] = None  # "auto", "knowledge_qa", "ship30_writer", "artifact_generator"

class ChatResponse(BaseModel):
    session_id: str
    message_id: str
    role: str = "assistant"
    content: str
    skill: str
    provider_used: str
    model_used: str
    citations: List[Citation] = []
    artifact: Optional[ArtifactResponse] = None
    created_at: datetime.datetime
