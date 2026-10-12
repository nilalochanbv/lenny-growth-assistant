from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.app.db.session import get_db
from backend.app.schemas.session import (
    SessionCreate, 
    SessionResponse, 
    SessionDetailResponse, 
    MessageResponse
)
from backend.app.services.session_service import SessionService

router = APIRouter()

@router.post("/sessions", response_model=SessionResponse)
def create_session(data: SessionCreate, db: Session = Depends(get_db)):
    session = SessionService.create_session(db, data)
    return SessionResponse(
        id=session.id,
        title=session.title,
        provider=session.provider,
        model_name=session.model_name,
        created_at=session.created_at,
        updated_at=session.updated_at,
        message_count=0
    )

@router.get("/sessions", response_model=List[SessionResponse])
def list_sessions(db: Session = Depends(get_db)):
    return SessionService.list_sessions(db)

@router.get("/sessions/{session_id}", response_model=SessionDetailResponse)
def get_session(session_id: str, db: Session = Depends(get_db)):
    session = SessionService.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    messages = SessionService.get_messages(db, session_id)
    return SessionDetailResponse(
        id=session.id,
        title=session.title,
        provider=session.provider,
        model_name=session.model_name,
        created_at=session.created_at,
        updated_at=session.updated_at,
        messages=[
            MessageResponse(
                id=m.id,
                session_id=m.session_id,
                role=m.role,
                content=m.content,
                skill=m.skill,
                citations=m.citations or [],
                created_at=m.created_at
            ) for m in messages
        ]
    )

@router.get("/sessions/{session_id}/messages", response_model=List[MessageResponse])
def get_session_messages(session_id: str, db: Session = Depends(get_db)):
    messages = SessionService.get_messages(db, session_id)
    return [
        MessageResponse(
            id=m.id,
            session_id=m.session_id,
            role=m.role,
            content=m.content,
            skill=m.skill,
            citations=m.citations or [],
            created_at=m.created_at
        ) for m in messages
    ]

@router.delete("/sessions/{session_id}")
def delete_session(session_id: str, db: Session = Depends(get_db)):
    success = SessionService.delete_session(db, session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "success", "message": "Session deleted"}
