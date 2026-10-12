import uuid
import datetime
from typing import List, Optional
from sqlalchemy.orm import Session as DBSession
from backend.app.db.models import Session as SessionModel, Message as MessageModel
from backend.app.schemas.session import SessionCreate

class SessionService:
    @staticmethod
    def create_session(db: DBSession, data: SessionCreate) -> SessionModel:
        session_id = str(uuid.uuid4())
        session = SessionModel(
            id=session_id,
            title=data.title or "New Conversation",
            provider=data.provider or "local",
            model_name=data.model_name or "qwen2.5:0.5b"
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def get_session(db: DBSession, session_id: str) -> Optional[SessionModel]:
        return db.query(SessionModel).filter(SessionModel.id == session_id).first()

    @staticmethod
    def list_sessions(db: DBSession, limit: int = 50) -> List[dict]:
        sessions = db.query(SessionModel).order_by(SessionModel.updated_at.desc()).limit(limit).all()
        result = []
        for s in sessions:
            msg_count = db.query(MessageModel).filter(MessageModel.session_id == s.id).count()
            result.append({
                "id": s.id,
                "title": s.title,
                "provider": s.provider,
                "model_name": s.model_name,
                "created_at": s.created_at,
                "updated_at": s.updated_at,
                "message_count": msg_count
            })
        return result

    @staticmethod
    def delete_session(db: DBSession, session_id: str) -> bool:
        session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if not session:
            return False
        db.delete(session)
        db.commit()
        return True

    @staticmethod
    def update_session_title(db: DBSession, session_id: str, title: str):
        session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if session:
            session.title = title
            session.updated_at = datetime.datetime.utcnow()
            db.commit()

    @staticmethod
    def add_message(
        db: DBSession, 
        session_id: str, 
        role: str, 
        content: str, 
        skill: Optional[str] = None, 
        citations: Optional[List[dict]] = None
    ) -> MessageModel:
        msg_id = str(uuid.uuid4())
        message = MessageModel(
            id=msg_id,
            session_id=session_id,
            role=role,
            content=content,
            skill=skill,
            citations=citations or []
        )
        db.add(message)
        
        # update session updated_at
        session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if session:
            session.updated_at = datetime.datetime.utcnow()
            
        db.commit()
        db.refresh(message)
        return message

    @staticmethod
    def get_messages(db: DBSession, session_id: str) -> List[MessageModel]:
        return db.query(MessageModel).filter(MessageModel.session_id == session_id).order_by(MessageModel.created_at.asc()).all()
