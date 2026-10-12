from pydantic import BaseModel
from typing import Optional, List

class Citation(BaseModel):
    chunk_id: str
    doc_title: str
    doc_url: str
    speaker: Optional[str] = None
    date: Optional[str] = None
    guest: Optional[str] = None
    excerpt: str
    score: float

class RetrievalResult(BaseModel):
    query: str
    citations: List[Citation]
    is_empty: bool = False
    message: Optional[str] = None
