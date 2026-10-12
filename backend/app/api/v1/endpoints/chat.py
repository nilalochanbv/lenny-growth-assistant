from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.schemas.chat import ChatRequest, ChatResponse
from backend.app.schemas.session import SessionCreate
from backend.app.services.session_service import SessionService
from backend.app.agents.orchestrator import AgentOrchestrator

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def process_chat(req: ChatRequest, db: Session = Depends(get_db)):
    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    # If no session_id provided, create one automatically
    session_id = req.session_id
    if not session_id:
        new_session = SessionService.create_session(
            db, 
            SessionCreate(
                title="New Conversation",
                provider=req.provider or "local",
                model_name=req.model_name
            )
        )
        session_id = new_session.id
    else:
        # Verify session exists
        existing = SessionService.get_session(db, session_id)
        if not existing:
            new_session = SessionService.create_session(
                db, 
                SessionCreate(
                    title="New Conversation",
                    provider=req.provider or "local",
                    model_name=req.model_name
                )
            )
            session_id = new_session.id

    result = await AgentOrchestrator.process_chat(
        db=db,
        session_id=session_id,
        user_message=req.message.strip(),
        provider_preference=req.provider,
        model_name=req.model_name,
        requested_skill=req.skill
    )

    return ChatResponse(**result)
